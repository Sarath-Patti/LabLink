"""
Unit tests for VLANHeader 802.1Q tagging.
"""

import pytest

from lablink.exceptions import InvalidVLANError
from lablink.network.vlan import VLANHeader


def test_vlan_header_serialization_and_parsing() -> None:
    """Verify 4-byte 802.1Q VLAN header serialization and parsing."""
    vlan = VLANHeader(vlan_id=100, pcp=3, dei=True)
    raw = vlan.to_bytes()

    assert len(raw) == 4
    parsed, remaining = VLANHeader.parse(raw + b"PAYLOAD")

    assert parsed.vlan_id == 100
    assert parsed.pcp == 3
    assert parsed.dei is True
    assert parsed.tpid == 0x8100
    assert remaining == b"PAYLOAD"


def test_vlan_header_invalid_id_raises() -> None:
    """Verify InvalidVLANError raised for out-of-range VLAN IDs."""
    with pytest.raises(InvalidVLANError, match="must be in range 0..4095"):
        VLANHeader(vlan_id=-1)

    with pytest.raises(InvalidVLANError, match="must be in range 0..4095"):
        VLANHeader(vlan_id=4096)


def test_vlan_header_invalid_pcp_raises() -> None:
    """Verify InvalidVLANError raised for out-of-range PCP priority."""
    with pytest.raises(InvalidVLANError, match="PCP priority must be in range 0..7"):
        VLANHeader(vlan_id=10, pcp=8)
