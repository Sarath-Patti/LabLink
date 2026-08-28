"""
Global Pytest Configuration and Reusable Test Fixtures for LabLink.

Provides reusable fixtures for simulator lifecycles, connected instrument clients,
Layer-2 Ethernet framing, software traffic engines, and mock transports.
"""

from collections.abc import Generator

import pytest

from lablink.config import LabLinkConfig
from lablink.devices.network_switch import NetworkSwitch
from lablink.instruments.optical_oscilloscope import OpticalOscilloscope
from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from lablink.network.ethernet import EthernetFrame
from lablink.network.mac import MACAddress
from lablink.network.traffic import TrafficGenerator, TrafficSink
from lablink.network.vlan import VLANHeader
from lablink.protocols.scpi import SCPIProtocol
from lablink.simulators.network_switch import NetworkSwitchSimulator
from lablink.simulators.optical_oscilloscope import OpticalOscilloscopeSimulator
from lablink.simulators.optical_power_meter import OpticalPowerMeterSimulator
from lablink.simulators.optical_switch import OpticalSwitchSimulator
from lablink.transport.mock import MockTransport
from lablink.transport.tcp import TCPTransport


@pytest.fixture
def test_config() -> LabLinkConfig:
    """Fixture providing environment configuration settings."""
    return LabLinkConfig.from_env()


@pytest.fixture
def mock_transport() -> MockTransport:
    """Fixture providing an auto-connected in-memory MockTransport."""
    return MockTransport(auto_connect=True)


@pytest.fixture
def mock_scpi(mock_transport: MockTransport) -> SCPIProtocol:
    """Fixture providing an SCPIProtocol instance over MockTransport."""
    return SCPIProtocol(transport=mock_transport)


# =============================================================================
# Layer-2 Ethernet and Traffic Engine Fixtures
# =============================================================================


@pytest.fixture
def default_src_mac() -> MACAddress:
    """Fixture providing a standard test source MAC address."""
    return MACAddress("00:11:22:33:44:55")


@pytest.fixture
def default_dst_mac() -> MACAddress:
    """Fixture providing a standard test destination MAC address."""
    return MACAddress("00:AA:BB:CC:DD:EE")


@pytest.fixture
def sample_ethernet_frame(
    default_src_mac: MACAddress, default_dst_mac: MACAddress
) -> EthernetFrame:
    """Fixture providing a sample VLAN-tagged EthernetFrame."""
    return EthernetFrame(
        dst_mac=default_dst_mac,
        src_mac=default_src_mac,
        ethertype=0x0800,
        vlan_header=VLANHeader(vlan_id=100, pcp=3),
        payload=b"LABLINK_L2_TEST_PAYLOAD",
    )


@pytest.fixture
def traffic_generator(default_src_mac: MACAddress, default_dst_mac: MACAddress) -> TrafficGenerator:
    """Fixture providing a configured TrafficGenerator instance."""
    return TrafficGenerator(
        src_mac=default_src_mac,
        dst_mac=default_dst_mac,
        vlan_id=100,
        frame_size=64,
        packet_count=50,
        rate_fps=1000.0,
    )


@pytest.fixture
def traffic_sink() -> TrafficSink:
    """Fixture providing a fresh TrafficSink instance."""
    return TrafficSink()


# =============================================================================
# Local Simulator Lifecycle Fixtures (127.0.0.1 with dynamic OS port)
# =============================================================================


@pytest.fixture
def opm_sim() -> Generator[OpticalPowerMeterSimulator, None, None]:
    """Fixture launching an OpticalPowerMeterSimulator on 127.0.0.1."""
    sim = OpticalPowerMeterSimulator(port=0, initial_wavelength_nm=1310.0, initial_power_dbm=-10.0)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def switch_sim() -> Generator[OpticalSwitchSimulator, None, None]:
    """Fixture launching an OpticalSwitchSimulator on 127.0.0.1."""
    sim = OpticalSwitchSimulator(port=0, channel_count=8, initial_route=1)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def scope_sim() -> Generator[OpticalOscilloscopeSimulator, None, None]:
    """Fixture launching an OpticalOscilloscopeSimulator on 127.0.0.1."""
    sim = OpticalOscilloscopeSimulator(port=0, sample_count=50)
    sim.start()
    yield sim
    sim.stop()


@pytest.fixture
def net_switch_sim() -> Generator[NetworkSwitchSimulator, None, None]:
    """Fixture launching a NetworkSwitchSimulator on 127.0.0.1."""
    sim = NetworkSwitchSimulator(port=0, port_count=24)
    sim.start()
    yield sim
    sim.stop()


# =============================================================================
# Connected Client Instrument Drivers Fixtures
# =============================================================================


@pytest.fixture
def opm_client(
    opm_sim: OpticalPowerMeterSimulator,
) -> Generator[OpticalPowerMeter, None, None]:
    """Fixture providing a connected OpticalPowerMeter client targeting opm_sim."""
    host, port = opm_sim.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    opm = OpticalPowerMeter(transport=transport)
    opm.connect()
    yield opm
    opm.disconnect()


@pytest.fixture
def switch_client(
    switch_sim: OpticalSwitchSimulator,
) -> Generator[OpticalSwitch, None, None]:
    """Fixture providing a connected OpticalSwitch client targeting switch_sim."""
    host, port = switch_sim.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    sw = OpticalSwitch(transport=transport)
    sw.connect()
    yield sw
    sw.disconnect()


@pytest.fixture
def scope_client(
    scope_sim: OpticalOscilloscopeSimulator,
) -> Generator[OpticalOscilloscope, None, None]:
    """Fixture providing a connected OpticalOscilloscope client targeting scope_sim."""
    host, port = scope_sim.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    scope = OpticalOscilloscope(transport=transport)
    scope.connect()
    yield scope
    scope.disconnect()


@pytest.fixture
def net_switch_client(
    net_switch_sim: NetworkSwitchSimulator,
) -> Generator[NetworkSwitch, None, None]:
    """Fixture providing a connected NetworkSwitch client targeting net_switch_sim."""
    host, port = net_switch_sim.server_address
    transport = TCPTransport(host=host, port=port, timeout=2.0)
    net_switch = NetworkSwitch(transport=transport)
    net_switch.connect()
    yield net_switch
    net_switch.disconnect()
