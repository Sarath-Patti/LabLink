"""
Negative Test Suite for Error Handling and Boundary Testing.

Verifies exception propagation, invalid parameter handling, SCPI error queue responses,
and transport failure modes.
"""

import pytest

from lablink.devices.network_switch import NetworkSwitch
from lablink.exceptions import DisconnectedTransportError, SCPIError
from lablink.instruments.optical_oscilloscope import OpticalOscilloscope
from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from lablink.transport.tcp import TCPTransport


@pytest.mark.negative
def test_opm_invalid_wavelength_negative(opm_client: OpticalPowerMeter) -> None:
    """Verify set_wavelength raises ValueError for negative wavelength."""
    with pytest.raises(ValueError, match="must be positive"):
        opm_client.set_wavelength(-100.0)


@pytest.mark.negative
def test_opm_invalid_unit_negative(opm_client: OpticalPowerMeter) -> None:
    """Verify set_unit raises ValueError for unsupported measurement unit."""
    with pytest.raises(ValueError, match="Unsupported unit"):
        opm_client.set_unit("INVALID_UNIT")


@pytest.mark.negative
def test_optical_switch_invalid_channel_negative(switch_client: OpticalSwitch) -> None:
    """Verify set_route raises ValueError for channel <= 0."""
    with pytest.raises(ValueError, match="must be >= 1"):
        switch_client.set_route(0)


@pytest.mark.negative
def test_scope_invalid_timebase_negative(scope_client: OpticalOscilloscope) -> None:
    """Verify set_timebase_scale raises ValueError for scale <= 0."""
    with pytest.raises(ValueError, match="must be positive"):
        scope_client.set_timebase_scale(-1.0)


@pytest.mark.negative
def test_network_switch_invalid_port_negative(net_switch_client: NetworkSwitch) -> None:
    """Verify enable_port raises ValueError for port <= 0."""
    with pytest.raises(ValueError, match="must be >= 1"):
        net_switch_client.enable_port(0)


@pytest.mark.negative
def test_undefined_scpi_command_raises_scpi_error(opm_client: OpticalPowerMeter) -> None:
    """Verify undefined SCPI command pushes -113 error to queue and raises SCPIError."""
    opm_client.write("UNDEFINED:HEADER:CMD")
    with pytest.raises(SCPIError, match="Undefined header"):
        opm_client.check_system_errors()


@pytest.mark.negative
def test_scope_waveform_disabled_acquisition_negative(
    scope_client: OpticalOscilloscope,
) -> None:
    """Verify acquiring waveform when acquisition is disabled pushes SCPI error and raises on error check."""
    scope_client.set_acquisition_state(False)
    scope_client.acquire_waveform()
    with pytest.raises(SCPIError, match="Settings conflict"):
        scope_client.check_system_errors()


@pytest.mark.negative
def test_disconnected_transport_raises_error() -> None:
    """Verify operating on disconnected transport raises DisconnectedTransportError."""
    transport = TCPTransport(host="127.0.0.1", port=9999, timeout=1.0)
    opm = OpticalPowerMeter(transport=transport)

    assert not opm.is_connected
    with pytest.raises(DisconnectedTransportError):
        opm.identify()
