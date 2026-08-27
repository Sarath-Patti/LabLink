"""
LabLink Network Switch Device Control Abstraction.

Provides device-level management for network switch port configuration and status control.
Establishes the device control layer without raw Layer-2 Ethernet packet generation.
"""

from lablink.instruments.base import BaseInstrument
from lablink.logging import get_logger
from lablink.protocols.scpi import SCPIProtocol

logger = get_logger("devices.network_switch")


class NetworkSwitch(BaseInstrument):
    """
    Software representation of a Network Switch device for port control.
    """

    def get_port_count(self) -> int:
        """
        Query total number of Ethernet ports available on the switch.

        Returns:
            Total port count integer.
        """
        resp = self.query("PORT:COUNT?")
        return int(resp.strip())

    def enable_port(self, port_num: int) -> None:
        """
        Enable specified network switch port.

        Args:
            port_num: 1-indexed port number integer.
        """
        if port_num < 1:
            raise ValueError(f"Invalid port number {port_num}; must be >= 1.")

        logger.info(f"Enabling Network Switch port {port_num}")
        self.write(f"PORT:ENABLE {port_num}")

    def disable_port(self, port_num: int) -> None:
        """
        Disable specified network switch port.

        Args:
            port_num: 1-indexed port number integer.
        """
        if port_num < 1:
            raise ValueError(f"Invalid port number {port_num}; must be >= 1.")

        logger.info(f"Disabling Network Switch port {port_num}")
        self.write(f"PORT:DISABLE {port_num}")

    def get_port_state(self, port_num: int) -> bool:
        """
        Query administrative operational state of specified network switch port.

        Args:
            port_num: 1-indexed port number integer.

        Returns:
            True if port is UP/enabled, False if DOWN/disabled.
        """
        if port_num < 1:
            raise ValueError(f"Invalid port number {port_num}; must be >= 1.")

        resp = self.query(f"PORT:STATE? {port_num}")
        return SCPIProtocol.parse_boolean(resp)

    def get_all_port_states(self) -> dict[int, bool]:
        """
        Query operational states for all ports on the switch.

        Returns:
            Dictionary mapping port_num (int) to state (bool).
        """
        resp = self.query("PORT:ALL?")
        if not resp:
            return {}

        port_states: dict[int, bool] = {}
        items = SCPIProtocol.parse_comma_separated(resp)
        for item in items:
            if ":" in item:
                port_str, state_str = item.split(":", 1)
                try:
                    port_num = int(port_str.strip())
                    is_up = state_str.strip().upper() in ("1", "UP", "ON", "TRUE")
                    port_states[port_num] = is_up
                except ValueError:
                    continue
        return port_states
