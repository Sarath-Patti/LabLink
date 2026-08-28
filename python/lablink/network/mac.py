"""
LabLink MAC Address Value Object.

Provides validated MAC address parsing, canonical string formatting, byte serialization,
equality comparison, and broadcast/multicast classification.
"""

import re

from lablink.exceptions import InvalidMACAddressError

MAC_REGEX = re.compile(r"^(?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}$|^[0-9a-fA-F]{12}$")


class MACAddress:
    """
    Validated IEEE 802 Media Access Control (MAC) address abstraction.
    """

    def __init__(self, address: "str | bytes | MACAddress") -> None:
        if isinstance(address, MACAddress):
            self._bytes: bytes = address._bytes
            return

        if isinstance(address, bytes):
            if len(address) != 6:
                raise InvalidMACAddressError(
                    f"MAC address byte length must be 6, got {len(address)}"
                )
            self._bytes = address
            return

        if isinstance(address, str):
            clean_str = address.strip()
            if not MAC_REGEX.match(clean_str):
                raise InvalidMACAddressError(f"Invalid MAC address format: {address!r}")

            hex_digits = clean_str.replace(":", "").replace("-", "")
            self._bytes = bytes.fromhex(hex_digits)
            return

        raise InvalidMACAddressError(
            f"Unsupported type for MACAddress initialization: {type(address).__name__}"
        )

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> "MACAddress":
        """Construct MACAddress from 6-byte sequence."""
        return cls(raw_bytes)

    def to_bytes(self) -> bytes:
        """Return 6-byte raw representation of MAC address."""
        return self._bytes

    def to_string(self) -> str:
        """Return canonical lowercase colon-separated string representation (00:11:22:33:44:55)."""
        return ":".join(f"{b:02x}" for b in self._bytes)

    @property
    def is_broadcast(self) -> bool:
        """Return True if MAC address is Ethernet broadcast (ff:ff:ff:ff:ff:ff)."""
        return self._bytes == b"\xff\xff\xff\xff\xff\xff"

    @property
    def is_multicast(self) -> bool:
        """Return True if MAC address least significant bit of first octet is set (and not broadcast)."""
        return (self._bytes[0] & 0x01 != 0) and not self.is_broadcast

    @property
    def is_unicast(self) -> bool:
        """Return True if MAC address is individual unicast."""
        return not (self.is_broadcast or self.is_multicast)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MACAddress):
            return self._bytes == other._bytes
        if isinstance(other, (str, bytes)):
            try:
                return self._bytes == MACAddress(other)._bytes
            except InvalidMACAddressError:
                return False
        return False

    def __hash__(self) -> int:
        return hash(self._bytes)

    def __repr__(self) -> str:
        return f"MACAddress('{self.to_string()}')"

    def __str__(self) -> str:
        return self.to_string()


BROADCAST_MAC = MACAddress("ff:ff:ff:ff:ff:ff")
ZERO_MAC = MACAddress("00:00:00:00:00:00")
