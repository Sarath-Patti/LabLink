"""
Unit tests for software instrument simulator classes and SCPI command dispatchers.
"""

from lablink.simulators.base import BaseInstrumentSimulator
from lablink.simulators.network_switch import NetworkSwitchSimulator
from lablink.simulators.optical_oscilloscope import OpticalOscilloscopeSimulator
from lablink.simulators.optical_power_meter import OpticalPowerMeterSimulator
from lablink.simulators.optical_switch import OpticalSwitchSimulator


def test_base_simulator_error_queue() -> None:
    """Verify FIFO error queue mechanics on BaseInstrumentSimulator."""
    sim = BaseInstrumentSimulator()

    code, msg = sim.pop_error()
    assert code == 0
    assert msg == "No error"

    sim.push_error(-113, "Undefined header")
    sim.push_error(-222, "Data out of range")

    code1, msg1 = sim.pop_error()
    assert code1 == -113
    assert msg1 == "Undefined header"

    code2, msg2 = sim.pop_error()
    assert code2 == -222
    assert msg2 == "Data out of range"

    code3, msg3 = sim.pop_error()
    assert code3 == 0
    assert msg3 == "No error"


def test_optical_power_meter_simulator_dispatch() -> None:
    """Verify OpticalPowerMeterSimulator SCPI command handling."""
    sim = OpticalPowerMeterSimulator(initial_wavelength_nm=1310.0, initial_power_dbm=-5.0)

    assert sim._dispatch_command("*IDN?") == "Keysight,N5767A-OPM,OPM998877,v2.1\n"

    assert sim._dispatch_command("CONF:WAVELENGTH?") == "1310.00\n"
    sim._dispatch_command("CONF:WAVELENGTH 1550.0")
    assert sim.wavelength_nm == 1550.0
    assert sim._dispatch_command("CONF:WAVELENGTH?") == "1550.00\n"

    assert sim._dispatch_command("MEAS:POW?") == "-5.0000\n"

    # Test out-of-range error
    sim._dispatch_command("CONF:WAVELENGTH -100")
    assert sim._dispatch_command("SYST:ERR?") == '-222,"Data out of range"\n'


def test_optical_switch_simulator_dispatch() -> None:
    """Verify OpticalSwitchSimulator SCPI command handling."""
    sim = OpticalSwitchSimulator(channel_count=4, initial_route=1)

    assert sim._dispatch_command("ROUTE?") == "1\n"
    sim._dispatch_command("ROUTE:SET 3")
    assert sim.active_route == 3
    assert sim._dispatch_command("ROUTE?") == "3\n"

    # Test invalid channel route error
    sim._dispatch_command("ROUTE:SET 99")
    assert sim._dispatch_command("SYST:ERR?") == '-222,"Data out of range"\n'


def test_optical_oscilloscope_simulator_dispatch() -> None:
    """Verify OpticalOscilloscopeSimulator SCPI command handling."""
    sim = OpticalOscilloscopeSimulator(sample_count=10)

    assert sim._dispatch_command("ACQUIRE:STATE?") == "1\n"
    data_resp = sim._dispatch_command("WAVEFORM:DATA?")
    assert data_resp is not None
    samples = data_resp.strip().split(",")
    assert len(samples) == 10

    sim._dispatch_command("ACQUIRE:STATE OFF")
    assert sim._dispatch_command("ACQUIRE:STATE?") == "0\n"
    sim._dispatch_command("WAVEFORM:DATA?")
    assert sim._dispatch_command("SYST:ERR?") == '-221,"Settings conflict"\n'


def test_network_switch_simulator_dispatch() -> None:
    """Verify NetworkSwitchSimulator SCPI command handling."""
    sim = NetworkSwitchSimulator(port_count=8)

    assert sim._dispatch_command("PORT:COUNT?") == "8\n"
    assert sim._dispatch_command("PORT:STATE? 1") == "1\n"

    sim._dispatch_command("PORT:DISABLE 1")
    assert sim._dispatch_command("PORT:STATE? 1") == "0\n"

    sim._dispatch_command("PORT:ENABLE 1")
    assert sim._dispatch_command("PORT:STATE? 1") == "1\n"
