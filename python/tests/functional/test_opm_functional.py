"""
Functional test suite for OpticalPowerMeter instrument operations.
"""

import pytest

from lablink.instruments.optical_power_meter import OpticalPowerMeter
from tests.utilities.assertions import assert_within_tolerance


@pytest.mark.functional
@pytest.mark.instrument
def test_opm_identification(opm_client: OpticalPowerMeter) -> None:
    """Verify OpticalPowerMeter identification query."""
    idn = opm_client.identify()
    assert "N5767A-OPM" in idn


@pytest.mark.functional
@pytest.mark.instrument
@pytest.mark.parametrize("wavelength", [850.0, 1310.0, 1550.0, 1625.0])
def test_opm_wavelength_parameterized(opm_client: OpticalPowerMeter, wavelength: float) -> None:
    """Verify set_wavelength and get_wavelength across standard optical bands."""
    opm_client.set_wavelength(wavelength)
    current_wl = opm_client.get_wavelength()
    assert_within_tolerance(current_wl, wavelength, 0.01, "Wavelength mismatch")


@pytest.mark.functional
@pytest.mark.instrument
@pytest.mark.parametrize("unit", ["DBM", "MW", "W"])
def test_opm_unit_parameterized(opm_client: OpticalPowerMeter, unit: str) -> None:
    """Verify set_unit and get_unit across supported power units."""
    opm_client.set_unit(unit)
    assert opm_client.get_unit() == unit


@pytest.mark.functional
@pytest.mark.instrument
def test_opm_power_measurement(opm_client: OpticalPowerMeter) -> None:
    """Verify optical power measurement reading."""
    power = opm_client.measure_power()
    assert_within_tolerance(power, -10.0, 0.001, "Power measurement mismatch")
