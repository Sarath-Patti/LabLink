"""
Unit tests for EthernetFrame serialization and parsing.
"""

import pytest

from lablink.exceptions import MalformedFrameError
from lablink.network.ethernet import EthernetFrame
from lablink.network.mac import MACAddress
from lablink.network.vlan import VLANHeader


def test_untagged_ethernet_frame_roundtrip() -> None:
    """Verify untagged EthernetFrame serialization and parsing."""
    frame = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
        ethertype=0x0800,
        payload=b"UNTAGGED_PAYLOAD_TEST",
    )

    raw_bytes = frame.to_bytes()
    assert len(raw_bytes) == 6 + 6 + 2 + len(b"UNTAGGED_PAYLOAD_TEST")

    parsed = EthernetFrame.from_bytes(raw_bytes)
    assert parsed.dst_mac == MACAddress("00:AA:BB:CC:DD:EE")
    assert parsed.src_mac == MACAddress("00:11:22:33:44:55")
    assert parsed.ethertype == 0x0800
    assert not parsed.is_vlan_tagged
    assert parsed.payload == b"UNTAGGED_PAYLOAD_TEST"


def test_vlan_tagged_ethernet_frame_roundtrip() -> None:
    """Verify 802.1Q tagged EthernetFrame serialization and parsing."""
    frame = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
        ethertype=0x0800,
        vlan_header=VLANHeader(vlan_id=200, pcp=5),
        payload=b"VLAN_TAGGED_PAYLOAD",
    )

    raw_bytes = frame.to_bytes()
    assert len(raw_bytes) == 6 + 6 + 4 + 2 + len(b"VLAN_TAGGED_PAYLOAD")

    parsed = EthernetFrame.from_bytes(raw_bytes)
    assert parsed.is_vlan_tagged
    assert parsed.vlan_header is not None
    assert parsed.vlan_header.vlan_id == 200
    assert parsed.vlan_header.pcp == 5
    assert parsed.payload == b"VLAN_TAGGED_PAYLOAD"


def test_ethernet_frame_telemetry_embedding() -> None:
    """Verify embedding sequence numbers and timestamps into frame payload."""
    frame = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
    )
    frame.embed_telemetry(sequence_number=42, timestamp_ns=1700000000000000000)

    parsed = EthernetFrame.from_bytes(frame.to_bytes())
    assert parsed.sequence_number == 42
    assert parsed.timestamp_ns == 1700000000000000000


def test_truncated_ethernet_frame_raises_malformed() -> None:
    """Verify MalformedFrameError raised for truncated raw frame bytes."""
    with pytest.raises(MalformedFrameError, match="truncated"):
        EthernetFrame.from_bytes(b"\x00\x11\x22")
