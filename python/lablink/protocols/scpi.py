"""
LabLink SCPI (Standard Commands for Programmable Instruments) Protocol Handler.

Implements SCPI command formatting, response parsing, IEEE 488.2 common commands,
and instrument status error evaluation over any LabLink BaseTransport.
"""

from lablink.exceptions import InvalidResponseError, SCPIError
from lablink.logging import get_logger
from lablink.transport.base import BaseTransport

logger = get_logger("protocols.scpi")


class SCPIProtocol:
    """
    SCPI Protocol handler wrapping a BaseTransport communication instance.
    """

    def __init__(
        self,
        transport: BaseTransport,
        read_termination: str = "\n",
        write_termination: str = "\n",
        encoding: str = "utf-8",
    ) -> None:
        self.transport: BaseTransport = transport
        self.read_termination: str = read_termination
        self.write_termination: str = write_termination
        self.encoding: str = encoding

    def write(self, command: str) -> None:
        """
        Format and send a SCPI write command to the instrument.

        Args:
            command: SCPI command string (e.g., "*RST", "OUTP ON").
        """
        cmd_clean = command.strip("\r\n")
        formatted = f"{cmd_clean}{self.write_termination}"
        logger.debug(f"SCPI Write: {cmd_clean!r}")
        self.transport.write(formatted.encode(self.encoding))

    def read(self) -> str:
        """
        Read string response from instrument until read termination character is found.

        Returns:
            Decoded response string with termination stripped.
        """
        buffer = bytearray()
        term_bytes = self.read_termination.encode(self.encoding)

        while True:
            chunk = self.transport.read(size=1024)
            if not chunk:
                break
            buffer.extend(chunk)
            if term_bytes in buffer:
                break

        response = buffer.decode(self.encoding, errors="replace")
        if self.read_termination and response.endswith(self.read_termination):
            response = response[: -len(self.read_termination)]
        elif response.endswith("\r"):
            response = response[:-1]

        cleaned_response = response.strip("\r\n")
        logger.debug(f"SCPI Read: {cleaned_response!r}")
        return cleaned_response

    def query(self, command: str) -> str:
        """
        Execute a SCPI query (write command followed immediately by read response).

        Args:
            command: SCPI query command string ending in '?' (e.g., "*IDN?").

        Returns:
            Response string from instrument.
        """
        self.write(command)
        return self.read()

    # =========================================================================
    # Standard IEEE 488.2 Common Commands
    # =========================================================================

    def idn(self) -> str:
        """
        Query instrument identification using standard '*IDN?' command.

        Returns:
            Manufacturer, model, serial number, and firmware version string.
        """
        return self.query("*IDN?")

    def reset(self) -> None:
        """Reset instrument to factory default state using '*RST'."""
        self.write("*RST")

    def clear(self) -> None:
        """Clear instrument status bytes and error queue using '*CLS'."""
        self.write("*CLS")

    def get_system_error(self) -> tuple[int, str]:
        """
        Query instrument system error queue using 'SYST:ERR?'.

        Returns:
            Tuple of (error_code: int, error_message: str).
        """
        raw_response = self.query("SYST:ERR?")
        return self.parse_error_response(raw_response)

    def check_system_errors(self) -> None:
        """
        Query 'SYST:ERR?' and raise SCPIError if error code != 0.
        """
        code, message = self.get_system_error()
        if code != 0:
            logger.error(f"Instrument SCPI Error [{code}]: {message}")
            raise SCPIError(code, message)

    # =========================================================================
    # SCPI Response Parsing Helpers
    # =========================================================================

    @staticmethod
    def parse_error_response(response: str) -> tuple[int, str]:
        """
        Parse raw 'SYST:ERR?' response like '+0,"No error"' into (0, "No error").
        """
        if not response:
            raise InvalidResponseError("Empty response received for SCPI error query")

        parts = response.split(",", 1)
        try:
            code = int(parts[0].strip())
            msg = parts[1].strip().strip('"') if len(parts) > 1 else ""
            return code, msg
        except (ValueError, IndexError) as e:
            err_msg = f"Failed to parse SCPI error response '{response}'"
            raise InvalidResponseError(err_msg) from e

    @staticmethod
    def parse_numeric(response: str) -> float:
        """Parse numeric float value from SCPI response string."""
        try:
            return float(response.strip())
        except ValueError as e:
            err_msg = f"Cannot parse numeric float from response '{response}'"
            raise InvalidResponseError(err_msg) from e

    @staticmethod
    def parse_comma_separated(response: str) -> list[str]:
        """Parse comma-delimited string response into a list of strings."""
        if not response:
            return []
        return [item.strip().strip('"') for item in response.split(",")]

    @staticmethod
    def parse_boolean(response: str) -> bool:
        """Parse boolean flag from SCPI response ('1'/'0', 'ON'/'OFF', 'TRUE'/'FALSE')."""
        cleaned = response.strip().upper()
        if cleaned in ("1", "ON", "TRUE"):
            return True
        if cleaned in ("0", "OFF", "FALSE"):
            return False
        err_msg = f"Cannot parse boolean from SCPI response '{response}'"
        raise InvalidResponseError(err_msg)
