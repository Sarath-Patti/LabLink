"""
LabLink Network Switch Device Control Software Simulator.

Simulates a Network Switch SCPI control interface over a local TCP server endpoint.
Provides port state management (enable/disable/query) and Layer-2 port statistics tracking.
"""

from lablink.logging import get_logger
from lablink.simulators.base import BaseInstrumentSimulator

logger = get_logger("simulators.network_switch")


class NetworkSwitchSimulator(BaseInstrumentSimulator):
    """
    TCP SCPI simulator for a Network Switch device control interface.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        vendor: str = "Cisco-Sim",
        model: str = "Nexus-9000-Sim",
        serial_number: str = "NET554433",
        firmware_version: str = "v4.0",
        port_count: int = 24,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            vendor=vendor,
            model=model,
            serial_number=serial_number,
            firmware_version=firmware_version,
        )
        self.port_count: int = port_count
        self.ports: dict[int, bool] = {i: True for i in range(1, port_count + 1)}
        self.port_stats: dict[int, dict[str, int]] = {
            i: {"RX": 0, "TX": 0, "DROP": 0} for i in range(1, port_count + 1)
        }

    def reset_state(self) -> None:
        """Reset all network switch ports to enabled (UP) state and clear stats."""
        super().reset_state()
        self.ports = {i: True for i in range(1, self.port_count + 1)}
        self.port_stats = {i: {"RX": 0, "TX": 0, "DROP": 0} for i in range(1, self.port_count + 1)}

    def record_port_stat(self, port: int, stat_type: str, count: int = 1) -> None:
        """Record port frame counter statistic."""
        if 1 <= port <= self.port_count and stat_type in ("RX", "TX", "DROP"):
            self.port_stats[port][stat_type] += count

    def _handle_custom_command(self, cmd: str) -> str | None:
        cmd_upper = cmd.upper().strip()

        if cmd_upper == "PORT:COUNT?":
            return f"{self.port_count}\n"

        if cmd_upper.startswith("PORT:ENABLE "):
            val_str = cmd[12:].strip()
            try:
                p_num = int(val_str)
                if p_num < 1 or p_num > self.port_count:
                    self.push_error(-222, "Data out of range")
                else:
                    self.ports[p_num] = True
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper.startswith("PORT:DISABLE "):
            val_str = cmd[13:].strip()
            try:
                p_num = int(val_str)
                if p_num < 1 or p_num > self.port_count:
                    self.push_error(-222, "Data out of range")
                else:
                    self.ports[p_num] = False
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper.startswith("PORT:STATE? "):
            val_str = cmd[12:].strip()
            try:
                p_num = int(val_str)
                if p_num < 1 or p_num > self.port_count:
                    self.push_error(-222, "Data out of range")
                    return "\n"
                return "1\n" if self.ports.get(p_num, False) else "0\n"
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
                return "\n"

        if cmd_upper == "PORT:ALL?":
            items = [f"{p}:UP" if state else f"{p}:DOWN" for p, state in self.ports.items()]
            return f"{','.join(items)}\n"

        if cmd_upper.startswith("PORT:STATS? "):
            val_str = cmd[12:].strip()
            try:
                p_num = int(val_str)
                if p_num < 1 or p_num > self.port_count:
                    self.push_error(-222, "Data out of range")
                    return "\n"
                stats = self.port_stats.get(p_num, {"RX": 0, "TX": 0, "DROP": 0})
                return f"RX:{stats['RX']},TX:{stats['TX']},DROP:{stats['DROP']}\n"
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
                return "\n"

        if cmd_upper == "PORT:STATS:CLEAR":
            for p in self.port_stats:
                self.port_stats[p] = {"RX": 0, "TX": 0, "DROP": 0}
            return None

        self.push_error(-113, "Undefined header")
        return None
