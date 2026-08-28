"""
LabLink Layer-2 Ethernet Frame Abstraction.

Provides typed Ethernet MAC framing, 802.1Q VLAN tagging integration,
structured payload sequence tracking, binary serialization, and frame parsing.
"""

import struct
import time

from lablink.exceptions import MalformedFrameError
from lablink.network.mac import MACAddress
from lablink.network.vlan import VLANHeader

TELEMETRY_PREFIX: bytes = b"LLPKT:"


class EthernetFrame:
    """
    Representation of an Ethernet II / IEEE 802.3 MAC Frame.
    """

    def __init__(
        self,
        dst_mac: MACAddress | str | bytes,
        src_mac: MACAddress | str | bytes,
        ethertype: int = 0x0800,
        vlan_header: VLANHeader | None = None,
        payload: bytes = b"",
        sequence_number: int | None = None,
        timestamp_ns: int | None = None,
    ) -> None:
        self.dst_mac: MACAddress = (
            dst_mac if isinstance(dst_mac, MACAddress) else MACAddress(dst_mac)
        )
        self.src_mac: MACAddress = (
            src_mac if isinstance(src_mac, MACAddress) else MACAddress(src_mac)
        )
        self.ethertype: int = ethertype
        self.vlan_header: VLANHeader | None = vlan_header
        self.payload: bytes = payload
        self.sequence_number: int | None = sequence_number
        self.timestamp_ns: int | None = timestamp_ns

    @property
    def is_vlan_tagged(self) -> bool:
        """Return True if frame includes an 802.1Q VLAN tag header."""
        return self.vlan_header is not None

    @property
    def frame_size(self) -> int:
        """Return total binary frame length in bytes."""
        return len(self.to_bytes())

    def embed_telemetry(self, sequence_number: int, timestamp_ns: int | None = None) -> None:
        """
        Embed structured telemetry header (sequence ID + timestamp_ns) into payload.
        """
        self.sequence_number = sequence_number
        self.timestamp_ns = timestamp_ns if timestamp_ns is not None else time.time_ns()

        header = TELEMETRY_PREFIX + struct.pack(">QQ", self.sequence_number, self.timestamp_ns)
        # Retain any trailing custom payload bytes beyond header
        existing_extra = (
            self.payload[len(header) :] if self.payload.startswith(TELEMETRY_PREFIX) else b""
        )
        self.payload = header + existing_extra

    def to_bytes(self) -> bytes:
        """
        Serialize EthernetFrame to binary MAC frame bytes.

        Header structure:
        - Destination MAC (6 bytes)
        - Source MAC (6 bytes)
        - [Optional 802.1Q VLAN Tag (4 bytes)]
        - EtherType (2 bytes)
        - Payload (N bytes)
        """
        result = self.dst_mac.to_bytes() + self.src_mac.to_bytes()
        if self.vlan_header:
            result += self.vlan_header.to_bytes() + self.ethertype.to_bytes(2, "big")
        else:
            result += self.ethertype.to_bytes(2, "big")

        result += self.payload
        return result

    @classmethod
    def from_bytes(cls, data: bytes) -> "EthernetFrame":
        """
        Parse binary byte stream into EthernetFrame instance.

        Raises:
            MalformedFrameError: If frame data is shorter than minimum header length.
        """
        min_untagged = 14
        if len(data) < min_untagged:
            raise MalformedFrameError(
                f"Ethernet frame truncated: expected >= 14 bytes, got {len(data)}"
            )

        dst_mac = MACAddress(data[0:6])
        src_mac = MACAddress(data[6:12])

        # Check for 802.1Q VLAN Tag (0x8100)
        tag_or_ethertype = int.from_bytes(data[12:14], "big")
        vlan_header: VLANHeader | None = None

        if tag_or_ethertype == VLANHeader.TPID_8021Q:
            if len(data) < 18:
                raise MalformedFrameError(
                    f"VLAN tagged Ethernet frame truncated: expected >= 18 bytes, got {len(data)}"
                )
            vlan_header, _ = VLANHeader.parse(data[12:16])
            ethertype = int.from_bytes(data[16:18], "big")
            payload = data[18:]
        else:
            ethertype = tag_or_ethertype
            payload = data[14:]

        # Extract embedded telemetry if present
        seq_num: int | None = None
        ts_ns: int | None = None

        if payload.startswith(TELEMETRY_PREFIX) and len(payload) >= len(TELEMETRY_PREFIX) + 16:
            prefix_len = len(TELEMETRY_PREFIX)
            seq_num, ts_ns = struct.unpack(">QQ", payload[prefix_len : prefix_len + 16])

        return cls(
            dst_mac=dst_mac,
            src_mac=src_mac,
            ethertype=ethertype,
            vlan_header=vlan_header,
            payload=payload,
            sequence_number=seq_num,
            timestamp_ns=ts_ns,
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EthernetFrame):
            return self.to_bytes() == other.to_bytes()
        return False

    def __repr__(self) -> str:
        tag_info = f", vlan={self.vlan_header.vlan_id}" if self.vlan_header else ""
        seq_info = f", seq={self.sequence_number}" if self.sequence_number is not None else ""
        return (
            f"EthernetFrame(src='{self.src_mac}', dst='{self.dst_mac}', "
            f"type=0x{self.ethertype:04x}{tag_info}{seq_info}, size={self.frame_size})"
        )
