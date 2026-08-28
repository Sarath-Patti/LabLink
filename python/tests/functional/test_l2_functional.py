"""
Functional Test Suite for Layer-2 Ethernet and Network Validation.
"""

import pytest

from lablink.network.ethernet import EthernetFrame
from lablink.network.mac import BROADCAST_MAC, MACAddress
from lablink.network.traffic import TrafficGenerator, TrafficSink
from lablink.network.vlan import VLANHeader
from tests.utilities.assertions import assert_within_tolerance


@pytest.mark.l2
@pytest.mark.functional
def test_mac_address_canonical_functional() -> None:
    """Verify MAC address formatting and classification across test streams."""
    src = MACAddress("00:11:22:33:44:55")
    dst = MACAddress("00:aa:bb:cc:dd:ee")

    assert src.to_string() == "00:11:22:33:44:55"
    assert dst.to_string() == "00:aa:bb:cc:dd:ee"
    assert BROADCAST_MAC.is_broadcast


@pytest.mark.l2
@pytest.mark.functional
@pytest.mark.parametrize("vlan_id", [1, 100, 4094])
def test_vlan_tagged_ethernet_functional(vlan_id: int) -> None:
    """Verify VLAN tagged EthernetFrame serialization and parsing across standard VLAN IDs."""
    vlan = VLANHeader(vlan_id=vlan_id, pcp=3)
    frame = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
        ethertype=0x0800,
        vlan_header=vlan,
        payload=b"VLAN_FUNCTIONAL_STREAM",
    )

    parsed = EthernetFrame.from_bytes(frame.to_bytes())
    assert parsed.is_vlan_tagged
    assert parsed.vlan_header is not None
    assert parsed.vlan_header.vlan_id == vlan_id


@pytest.mark.l2
@pytest.mark.functional
@pytest.mark.parametrize("frame_size", [64, 128, 512, 1518])
def test_traffic_generator_frame_sizes_functional(frame_size: int) -> None:
    """Verify traffic generator produces exact target frame sizes."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        frame_size=frame_size,
        packet_count=5,
    )
    frames = gen.generate_frames()

    for frame in frames:
        assert frame.frame_size == frame_size


@pytest.mark.l2
@pytest.mark.functional
def test_end_to_end_traffic_stream_functional(
    traffic_generator: TrafficGenerator, traffic_sink: TrafficSink
) -> None:
    """Verify end-to-end software traffic generation and sink analysis."""
    frames = traffic_generator.generate_frames()
    tx_bytes = sum(f.frame_size for f in frames)

    for frame in frames:
        traffic_sink.process_frame(frame)

    stats = traffic_sink.analyze(
        transmitted_count=len(frames),
        transmitted_bytes=tx_bytes,
        duration_sec=0.1,
    )

    assert stats.transmitted_packets == 50
    assert stats.received_packets == 50
    assert stats.lost_packets == 0
    assert_within_tolerance(stats.packet_loss_percentage, 0.0, 0.001)
    assert stats.throughput_packets_per_sec > 0.0
