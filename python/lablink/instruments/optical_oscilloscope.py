"""
LabLink Optical Oscilloscope Instrument Abstraction.

Provides automated control for timebase scale, voltage/optical channel scale,
acquisition state, and waveform sample data retrieval.
"""

from dataclasses import dataclass

from lablink.instruments.base import BaseInstrument
from lablink.logging import get_logger
from lablink.protocols.scpi import SCPIProtocol

logger = get_logger("instruments.optical_oscilloscope")


@dataclass
class WaveformData:
    """Structured representation of acquired oscilloscope waveform sample data."""

    time_scale: float
    voltage_scale: float
    sample_rate_hz: float
    samples: list[float]


class OpticalOscilloscope(BaseInstrument):
    """
    Software representation of an Optical Oscilloscope test instrument.
    """

    def set_timebase_scale(self, seconds: float) -> None:
        """
        Configure oscilloscope horizontal timebase scale in seconds per division.

        Args:
            seconds: Timebase scale in seconds (must be positive).
        """
        if seconds <= 0:
            raise ValueError(f"Invalid timebase scale {seconds}; must be positive.")

        logger.info(f"Setting Optical Oscilloscope timebase scale to {seconds} s/div")
        self.write(f"TIMEBASE:SCALE {seconds}")

    def get_timebase_scale(self) -> float:
        """
        Query current configured timebase scale in seconds per division.

        Returns:
            Timebase scale float.
        """
        resp = self.query("TIMEBASE:SCALE?")
        return SCPIProtocol.parse_numeric(resp)

    def set_channel_scale(self, volts_per_div: float) -> None:
        """
        Configure oscilloscope vertical channel scale in volts/watts per division.

        Args:
            volts_per_div: Channel scale value (must be positive).
        """
        if volts_per_div <= 0:
            raise ValueError(f"Invalid channel scale {volts_per_div}; must be positive.")

        logger.info(f"Setting Optical Oscilloscope channel scale to {volts_per_div}/div")
        self.write(f"CHANNEL:SCALE {volts_per_div}")

    def get_channel_scale(self) -> float:
        """
        Query current configured channel scale in volts/watts per division.

        Returns:
            Channel scale float.
        """
        resp = self.query("CHANNEL:SCALE?")
        return SCPIProtocol.parse_numeric(resp)

    def set_acquisition_state(self, enabled: bool) -> None:
        """
        Enable or disable oscilloscope waveform acquisition.

        Args:
            enabled: True to start acquisition, False to stop.
        """
        state_str = "ON" if enabled else "OFF"
        logger.info(f"Setting Optical Oscilloscope acquisition state to {state_str}")
        self.write(f"ACQUIRE:STATE {state_str}")

    def get_acquisition_state(self) -> bool:
        """
        Query current waveform acquisition state.

        Returns:
            True if acquisition is active, False otherwise.
        """
        resp = self.query("ACQUIRE:STATE?")
        return SCPIProtocol.parse_boolean(resp)

    def acquire_waveform(self) -> WaveformData:
        """
        Acquire and retrieve structured waveform sample data from oscilloscope.

        Returns:
            WaveformData instance populated with timebase, channel scale, and sample array.
        """
        logger.debug("Acquiring waveform sample data from oscilloscope...")
        time_scale = self.get_timebase_scale()
        voltage_scale = self.get_channel_scale()

        raw_data = self.query("WAVEFORM:DATA?")
        items = SCPIProtocol.parse_comma_separated(raw_data)
        samples = [float(item) for item in items if item]

        # Estimate sample rate based on timebase scale and sample count
        sample_count = len(samples)
        total_time = time_scale * 10.0  # standard 10 division screen width
        sample_rate_hz = (sample_count / total_time) if total_time > 0 else 1e6

        logger.debug(f"Acquired {sample_count} waveform samples.")
        return WaveformData(
            time_scale=time_scale,
            voltage_scale=voltage_scale,
            sample_rate_hz=sample_rate_hz,
            samples=samples,
        )
