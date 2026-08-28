"""
Negative Test Suite for Layer-2 Ethernet and Network Validation.
"""

import pytest

from lablink.exceptions import InvalidMACAddressError, InvalidVLANError, MalformedFrameError
from lablink.network.ethernet import EthernetFrame
from lablink.network.mac import MACAddress
from lablink.network.traffic import TrafficGenerator, TrafficSink
from lablink.network.vlan import VLANHeader


@pytest.mark.l2
@pytest.mark.negative
def test_malformed_mac_address_negative() -> None:
    """Verify InvalidMACAddressError raised for invalid MAC strings."""
    with pytest.raises(InvalidMACAddressError):
        MACAddress("00:11:22")

    with pytest.raises(InvalidMACAddressError):
        MACAddress("ZZ:11:22:33:44:55")


@pytest.mark.l2
@pytest.mark.negative
def test_invalid_vlan_parameters_negative() -> None:
    """Verify InvalidVLANError raised for out-of-range VLAN ID and PCP."""
    with pytest.raises(InvalidVLANError):
        VLANHeader(vlan_id=4096)

    with pytest.raises(InvalidVLANError):
        VLANHeader(vlan_id=10, pcp=9)


@pytest.mark.l2
@pytest.mark.negative
def test_truncated_raw_ethernet_frames_negative() -> None:
    """Verify MalformedFrameError raised for truncated raw byte sequences."""
    with pytest.raises(MalformedFrameError, match="truncated"):
        EthernetFrame.from_bytes(b"\x00\x11\x22\x33")

    with pytest.raises(MalformedFrameError, match="truncated"):
        # 16 bytes raw with VLAN tag indicator 0x8100 but missing ethertype
        EthernetFrame.from_bytes(
            b"\x00\x11\x22\x33\x44\x55\x00\x11\x22\x33\x44\x55\x81\x00\x00\x64"
        )


@pytest.mark.l2
@pytest.mark.negative
def test_traffic_sink_corrupted_and_missing_sequences_negative() -> None:
    """Verify TrafficSink detects corrupted frames and calculates sequence loss."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        packet_count=10,
    )
    frames = gen.generate_frames()

    sink = TrafficSink()
    # Process frames 1..5, skip 6..8, process 9..10 (3 missing)
    for frame in frames[:5] + frames[8:]:
        sink.process_frame(frame)

    sink.process_bytes(b"CORRUPT")  # < 14 bytes truncated frame

    stats = sink.analyze(transmitted_count=10, transmitted_bytes=640, duration_sec=1.0)
    assert stats.lost_packets == 3
    assert stats.corrupted_packets == 1
