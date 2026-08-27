"""
End-to-End Integration Tests for Instrument Clients against Local TCP Simulators.

Runs real TCP socket communication between LabLink instrument classes (OpticalPowerMeter,
OpticalSwitch, OpticalOscilloscope, NetworkSwitch) and in-process TCP SCPI software
simulators listening on localhost (127.0.0.1).
"""

import pytest

from lablink.devices.network_switch import NetworkSwitch
from lablink.instruments.optical_oscilloscope import OpticalOscilloscope, WaveformData
from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from lablink.simulators.network_switch import NetworkSwitchSimulator
from lablink.simulators.optical_oscilloscope import OpticalOscilloscopeSimulator
from lablink.simulators.optical_power_meter import OpticalPowerMeterSimulator
from lablink.simulators.optical_switch import OpticalSwitchSimulator
from lablink.transport.tcp import TCPTransport


@pytest.fixture
def opm_simulator():
    """Fixture starting an in-process OpticalPowerMeterSimulator on 127.0.0.1."""
    sim = OpticalPowerMeterSimulator(
        port=0,
        initial_wavelength_nm=1310.0,
        initial_power_dbm=-15.5,
    )
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def switch_simulator():
    """Fixture starting an in-process OpticalSwitchSimulator on 127.0.0.1."""
    sim = OpticalSwitchSimulator(port=0, channel_count=8, initial_route=1)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def scope_simulator():
    """Fixture starting an in-process OpticalOscilloscopeSimulator on 127.0.0.1."""
    sim = OpticalOscilloscopeSimulator(port=0, sample_count=20)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def net_switch_simulator():
    """Fixture starting an in-process NetworkSwitchSimulator on 127.0.0.1."""
    sim = NetworkSwitchSimulator(port=0, port_count=12)
    sim.start()
    yield sim
    sim.stop()


def test_optical_power_meter_tcp_integration(opm_simulator) -> None:
    """Verify end-to-end OpticalPowerMeter client over TCP to simulator."""
    host, port = opm_simulator.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    opm = OpticalPowerMeter(transport=transport)

    opm.connect()
    assert opm.is_connected

    try:
        assert "N5767A-OPM" in opm.identify()

        assert opm.get_wavelength() == 1310.0
        opm.set_wavelength(1550.0)
        assert opm.get_wavelength() == 1550.0

        assert opm.measure_power() == -15.5

        opm.reset()
        assert opm.get_wavelength() == 1310.0

    finally:
        opm.disconnect()
        assert not opm.is_connected


def test_optical_switch_tcp_integration(switch_simulator) -> None:
    """Verify end-to-end OpticalSwitch client over TCP to simulator."""
    host, port = switch_simulator.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    opt_switch = OpticalSwitch(transport=transport)

    opt_switch.connect()
    assert opt_switch.is_connected

    try:
        assert "MAP-200-SW" in opt_switch.identify()

        assert opt_switch.get_channel_count() == 8
        assert opt_switch.get_route() == 1

        opt_switch.set_route(4)
        assert opt_switch.get_route() == 4

        opt_switch.reset()
        assert opt_switch.get_route() == 1

    finally:
        opt_switch.disconnect()
        assert not opt_switch.is_connected


def test_optical_oscilloscope_tcp_integration(scope_simulator) -> None:
    """Verify end-to-end OpticalOscilloscope client over TCP to simulator."""
    host, port = scope_simulator.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    scope = OpticalOscilloscope(transport=transport)

    scope.connect()
    assert scope.is_connected

    try:
        assert "MSO54-OPT" in scope.identify()

        scope.set_timebase_scale(2e-3)
        assert scope.get_timebase_scale() == 2e-3

        scope.set_channel_scale(1.0)
        assert scope.get_channel_scale() == 1.0

        wf = scope.acquire_waveform()
        assert isinstance(wf, WaveformData)
        assert len(wf.samples) == 20

    finally:
        scope.disconnect()
        assert not scope.is_connected


def test_network_switch_tcp_integration(net_switch_simulator) -> None:
    """Verify end-to-end NetworkSwitch client over TCP to simulator."""
    host, port = net_switch_simulator.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    net_switch = NetworkSwitch(transport=transport)

    net_switch.connect()
    assert net_switch.is_connected

    try:
        assert "Nexus-9000-Sim" in net_switch.identify()

        assert net_switch.get_port_count() == 12
        assert net_switch.get_port_state(1) is True

        net_switch.disable_port(1)
        assert net_switch.get_port_state(1) is False

        net_switch.enable_port(1)
        assert net_switch.get_port_state(1) is True

    finally:
        net_switch.disconnect()
        assert not net_switch.is_connected
