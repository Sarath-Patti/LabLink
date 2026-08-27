"""
LabLink Optical Power Meter Software Simulator.

Simulates an Optical Power Meter SCPI instrument over a local TCP server endpoint.
Provides deterministic power measurements, wavelength settings, unit management,
and optional Gaussian measurement noise simulation.
"""

import random

from lablink.logging import get_logger
from lablink.simulators.base import BaseInstrumentSimulator

logger = get_logger("simulators.optical_power_meter")


class OpticalPowerMeterSimulator(BaseInstrumentSimulator):
    """
    TCP SCPI simulator for an Optical Power Meter test instrument.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        vendor: str = "Keysight",
        model: str = "N5767A-OPM",
        serial_number: str = "OPM998877",
        firmware_version: str = "v2.1",
        initial_wavelength_nm: float = 1310.0,
        initial_power_dbm: float = -10.0,
        noise_stddev: float = 0.0,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            vendor=vendor,
            model=model,
            serial_number=serial_number,
            firmware_version=firmware_version,
        )
        self.initial_wavelength_nm: float = initial_wavelength_nm
        self.initial_power_dbm: float = initial_power_dbm
        self.noise_stddev: float = noise_stddev

        self.wavelength_nm: float = initial_wavelength_nm
        self.power_dbm: float = initial_power_dbm
        self.unit: str = "DBM"

    def reset_state(self) -> None:
        """Reset power meter state to initial default parameters."""
        super().reset_state()
        self.wavelength_nm = self.initial_wavelength_nm
        self.power_dbm = self.initial_power_dbm
        self.unit = "DBM"

    def _handle_custom_command(self, cmd: str) -> str | None:
        cmd_upper = cmd.upper().strip()

        if cmd_upper.startswith("CONF:WAVELENGTH "):
            val_str = cmd[16:].strip()
            try:
                val = float(val_str)
                if val <= 0:
                    self.push_error(-222, "Data out of range")
                else:
                    self.wavelength_nm = val
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "CONF:WAVELENGTH?":
            return f"{self.wavelength_nm:.2f}\n"

        if cmd_upper.startswith("CONF:UNIT "):
            target_unit = cmd[10:].strip().upper()
            if target_unit in ("DBM", "MW", "W"):
                self.unit = target_unit
            else:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "CONF:UNIT?":
            return f"{self.unit}\n"

        if cmd_upper == "MEAS:POW?":
            measured = self.power_dbm
            if self.noise_stddev > 0.0:
                measured += random.gauss(0.0, self.noise_stddev)
            return f"{measured:.4f}\n"

        self.push_error(-113, "Undefined header")
        return None
