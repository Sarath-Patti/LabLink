"""
LabLink Optical Oscilloscope Software Simulator.

Simulates an Optical Oscilloscope SCPI instrument over a local TCP server endpoint.
Provides deterministic waveform sample generation, timebase/channel scale configuration,
and acquisition state control.
"""

import math

from lablink.logging import get_logger
from lablink.simulators.base import BaseInstrumentSimulator

logger = get_logger("simulators.optical_oscilloscope")


class OpticalOscilloscopeSimulator(BaseInstrumentSimulator):
    """
    TCP SCPI simulator for an Optical Oscilloscope test instrument.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        vendor: str = "Tektronix",
        model: str = "MSO54-OPT",
        serial_number: str = "SCO776655",
        firmware_version: str = "v3.2",
        sample_count: int = 100,
        initial_time_scale: float = 1e-3,
        initial_voltage_scale: float = 0.5,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            vendor=vendor,
            model=model,
            serial_number=serial_number,
            firmware_version=firmware_version,
        )
        self.sample_count: int = sample_count
        self.initial_time_scale: float = initial_time_scale
        self.initial_voltage_scale: float = initial_voltage_scale

        self.time_scale: float = initial_time_scale
        self.voltage_scale: float = initial_voltage_scale
        self.acquisition_state: bool = True

    def reset_state(self) -> None:
        """Reset oscilloscope parameters to initial default values."""
        super().reset_state()
        self.time_scale = self.initial_time_scale
        self.voltage_scale = self.initial_voltage_scale
        self.acquisition_state = True

    def _handle_custom_command(self, cmd: str) -> str | None:
        cmd_upper = cmd.upper().strip()

        if cmd_upper.startswith("TIMEBASE:SCALE "):
            val_str = cmd[15:].strip()
            try:
                val = float(val_str)
                if val <= 0:
                    self.push_error(-222, "Data out of range")
                else:
                    self.time_scale = val
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "TIMEBASE:SCALE?":
            return f"{self.time_scale:.6e}\n"

        if cmd_upper.startswith("CHANNEL:SCALE "):
            val_str = cmd[14:].strip()
            try:
                val = float(val_str)
                if val <= 0:
                    self.push_error(-222, "Data out of range")
                else:
                    self.voltage_scale = val
            except ValueError:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "CHANNEL:SCALE?":
            return f"{self.voltage_scale:.4f}\n"

        if cmd_upper.startswith("ACQUIRE:STATE "):
            val_str = cmd[14:].strip().upper()
            if val_str in ("ON", "1", "TRUE"):
                self.acquisition_state = True
            elif val_str in ("OFF", "0", "FALSE"):
                self.acquisition_state = False
            else:
                self.push_error(-224, "Illegal parameter value")
            return None

        if cmd_upper == "ACQUIRE:STATE?":
            return "1\n" if self.acquisition_state else "0\n"

        if cmd_upper == "WAVEFORM:DATA?":
            if not self.acquisition_state:
                self.push_error(-221, "Settings conflict")
                return "\n"

            # Generate deterministic sine wave scaled by voltage_scale
            samples = [
                math.sin(2 * math.pi * i / 20.0) * self.voltage_scale
                for i in range(self.sample_count)
            ]
            formatted_samples = ",".join(f"{s:.4f}" for s in samples)
            return f"{formatted_samples}\n"

        self.push_error(-113, "Undefined header")
        return None
