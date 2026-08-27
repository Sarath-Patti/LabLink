"""
Unit tests for OpticalPowerMeter instrument control.
"""

import pytest

from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.transport.mock import MockTransport


def test_optical_power_meter_wavelength_config() -> None:
    """Verify set_wavelength and get_wavelength commands."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("CONF:WAVELENGTH?\n", "1550.00\n")

    opm = OpticalPowerMeter(transport=mock_transport)
    opm.set_wavelength(1550.0)
    assert mock_transport.written_history[-1] == b"CONF:WAVELENGTH 1550.0\n"

    wl = opm.get_wavelength()
    assert wl == 1550.0

    with pytest.raises(ValueError, match="must be positive"):
        opm.set_wavelength(-10.0)


def test_optical_power_meter_measurement_and_unit() -> None:
    """Verify measure_power and unit configuration commands."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("MEAS:POW?\n", "-12.4500\n")
    mock_transport.add_response("CONF:UNIT?\n", "MW\n")

    opm = OpticalPowerMeter(transport=mock_transport)

    power = opm.measure_power()
    assert power == -12.45

    opm.set_unit("mW")
    assert mock_transport.written_history[-1] == b"CONF:UNIT MW\n"

    unit = opm.get_unit()
    assert unit == "MW"

    with pytest.raises(ValueError, match="Unsupported unit"):
        opm.set_unit("INVALID_UNIT")
