"""
Unit tests for MACAddress value object.
"""

import pytest

from lablink.exceptions import InvalidMACAddressError
from lablink.network.mac import BROADCAST_MAC, ZERO_MAC, MACAddress


def test_mac_address_string_formatting() -> None:
    """Verify MAC address parsing from colon, hyphen, and raw hex strings."""
    mac1 = MACAddress("00:11:22:33:44:55")
    mac2 = MACAddress("00-11-22-33-44-55")
    mac3 = MACAddress("001122334455")

    assert mac1.to_string() == "00:11:22:33:44:55"
    assert mac2.to_string() == "00:11:22:33:44:55"
    assert mac3.to_string() == "00:11:22:33:44:55"
    assert mac1 == mac2 == mac3


def test_mac_address_bytes_serialization() -> None:
    """Verify MACAddress byte serialization and constructor from bytes."""
    expected_bytes = b"\x00\x11\x22\x33\x44\x55"
    mac = MACAddress(expected_bytes)

    assert mac.to_bytes() == expected_bytes
    assert MACAddress.from_bytes(expected_bytes) == mac


def test_mac_address_classifications() -> None:
    """Verify unicast, multicast, and broadcast classifications."""
    unicast = MACAddress("00:11:22:33:44:55")
    assert unicast.is_unicast
    assert not unicast.is_multicast
    assert not unicast.is_broadcast

    multicast = MACAddress("01:80:c2:00:00:00")
    assert multicast.is_multicast
    assert not multicast.is_unicast
    assert not multicast.is_broadcast

    assert BROADCAST_MAC.is_broadcast
    assert not BROADCAST_MAC.is_unicast
    assert not BROADCAST_MAC.is_multicast

    assert ZERO_MAC.to_string() == "00:00:00:00:00:00"


def test_mac_address_invalid_format_raises() -> None:
    """Verify InvalidMACAddressError raised for malformed MAC strings or bytes."""
    with pytest.raises(InvalidMACAddressError, match="Invalid MAC address format"):
        MACAddress("00:11:22:33:44")

    with pytest.raises(InvalidMACAddressError, match="Invalid MAC address format"):
        MACAddress("INVALID_MAC_STRING")

    with pytest.raises(InvalidMACAddressError, match="must be 6"):
        MACAddress(b"\x00\x11")
