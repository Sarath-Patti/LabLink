"""
LabLink Base Instrument Abstraction.

Provides common instrument Lifecycle management, SCPI protocol delegation,
status evaluation, and transport composition.
"""

from abc import ABC

from lablink.logging import get_logger
from lablink.protocols.scpi import SCPIProtocol
from lablink.transport.base import BaseTransport
from lablink.transport.mock import MockTransport

logger = get_logger("instruments.base")


class BaseInstrument(ABC):
    """
    Abstract Base Class for all LabLink instruments.

    Composes a BaseTransport communication instance and SCPIProtocol handler.
    """

    def __init__(self, transport: BaseTransport | None = None) -> None:
        self.transport: BaseTransport = transport or MockTransport()
        self.scpi: SCPIProtocol = SCPIProtocol(transport=self.transport)

    @property
    def is_connected(self) -> bool:
        """Return True if underlying transport is currently connected."""
        return self.transport.is_connected

    @property
    def timeout(self) -> float:
        """Return instrument transport operation timeout in seconds."""
        return self.transport.timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set instrument transport operation timeout in seconds."""
        self.transport.timeout = value

    def connect(self) -> None:
        """Connect to underlying instrument transport."""
        logger.info(f"Connecting instrument over {self.transport.__class__.__name__}...")
        self.transport.connect()

    def disconnect(self) -> None:
        """Disconnect underlying instrument transport."""
        logger.info(f"Disconnecting instrument over {self.transport.__class__.__name__}...")
        self.transport.disconnect()

    def write(self, command: str) -> None:
        """Write SCPI command string to instrument."""
        self.scpi.write(command)

    def read(self) -> str:
        """Read SCPI response string from instrument."""
        return self.scpi.read()

    def query(self, command: str) -> str:
        """Query instrument with SCPI command and return string response."""
        return self.scpi.query(command)

    def identify(self) -> str:
        """Query instrument identification via standard *IDN?."""
        return self.scpi.idn()

    def reset(self) -> None:
        """Reset instrument to default factory state via *RST."""
        logger.info("Resetting instrument state (*RST)...")
        self.scpi.reset()

    def clear(self) -> None:
        """Clear instrument status register and error queue via *CLS."""
        logger.info("Clearing instrument status register (*CLS)...")
        self.scpi.clear()

    def get_system_error(self) -> tuple[int, str]:
        """Query system error queue using SYST:ERR?."""
        return self.scpi.get_system_error()

    def check_system_errors(self) -> None:
        """Query system error queue and raise SCPIError if error code != 0."""
        self.scpi.check_system_errors()
