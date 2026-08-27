"""
LabLink Optical Power Meter Instrument Abstraction.

Provides automated control for optical power measurement, wavelength configuration,
and measurement unit settings over SCPI protocol and BaseTransport.
"""

from lablink.instruments.base import BaseInstrument
from lablink.logging import get_logger
from lablink.protocols.scpi import SCPIProtocol

logger = get_logger("instruments.optical_power_meter")


class OpticalPowerMeter(BaseInstrument):
    """
    Software representation of an Optical Power Meter test instrument.
    """

    SUPPORTED_UNITS = ("DBM", "MW", "W")

    def set_wavelength(self, wavelength_nm: float) -> None:
        """
        Configure target optical measurement wavelength in nanometers (nm).

        Args:
            wavelength_nm: Wavelength in nanometers (must be positive).
        """
        if wavelength_nm <= 0:
            raise ValueError(f"Invalid wavelength {wavelength_nm} nm; must be positive.")

        logger.info(f"Setting Optical Power Meter wavelength to {wavelength_nm} nm")
        self.write(f"CONF:WAVELENGTH {wavelength_nm}")

    def get_wavelength(self) -> float:
        """
        Query current configured measurement wavelength in nanometers (nm).

        Returns:
            Configured wavelength in nanometers.
        """
        resp = self.query("CONF:WAVELENGTH?")
        return SCPIProtocol.parse_numeric(resp)

    def measure_power(self) -> float:
        """
        Execute optical power measurement.

        Returns:
            Measured optical power value (in configured unit, default dBm).
        """
        logger.debug("Executing optical power measurement...")
        resp = self.query("MEAS:POW?")
        power = SCPIProtocol.parse_numeric(resp)
        logger.debug(f"Optical power measurement result: {power}")
        return power

    def set_unit(self, unit: str) -> None:
        """
        Configure power measurement unit ('DBM', 'MW', 'W').

        Args:
            unit: Power unit string.
        """
        unit_upper = unit.strip().upper()
        if unit_upper not in self.SUPPORTED_UNITS:
            raise ValueError(f"Unsupported unit '{unit}'; must be one of {self.SUPPORTED_UNITS}")

        logger.info(f"Setting Optical Power Meter measurement unit to '{unit_upper}'")
        self.write(f"CONF:UNIT {unit_upper}")

    def get_unit(self) -> str:
        """
        Query configured optical power measurement unit.

        Returns:
            Configured unit string ('DBM', 'MW', or 'W').
        """
        return self.query("CONF:UNIT?").strip().upper()
