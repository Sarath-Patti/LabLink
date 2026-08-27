"""
LabLink Optical Switch Software Simulator.

Simulates an Optical Switch SCPI instrument over a local TCP server endpoint.
Provides deterministic channel routing, port count queries, and out-of-range error handling.
"""

from lablink.logging import get_logger
from lablink.simulators.base import BaseInstrumentSimulator

logger = get_logger("simulators.optical_switch")


class OpticalSwitchSimulator(BaseInstrumentSimulator):
    """
    TCP SCPI simulator for an Optical Switch test instrument.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        vendor: str = "Viavi",
        model: str = "MAP-200-SW",
        serial_number: str = "SW112233",
        firmware_version: str = "v1.5",
        channel_count: int = 8,
        initial_route: int = 1,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            vendor=vendor,
            model=model,
            serial_number=serial_number,
            firmware_version=firmware_version,
        )
        self.channel_count: int = channel_count
        self.initial_route: int = initial_route
        self.active_route: int = initial_route

    def reset_state(self) -> None:
        """Reset optical switch active route to initial channel."""
        super().reset_state()
        self.active_route = self.initial_route

    def _handle_custom_command(self, cmd: str) -> str | None:
        cmd_upper = cmd.upper().strip()

        if cmd_upper.startswith("ROUTE:SET "):
            val_str = cmd[10:].strip()
            try:
                channel = int(val_str)
                if channel < 1 or channel > self.channel_count:
                    self.push_error(-222, "Data out of range")
                else:
                    self.active_route = channel
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "ROUTE?":
            return f"{self.active_route}\n"

        if cmd_upper == "ROUTE:CHAN:COUNT?":
            return f"{self.channel_count}\n"

        self.push_error(-113, "Undefined header")
        return None
