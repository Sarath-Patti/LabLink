"""
LabLink IEEE 802.1Q VLAN Tagging Abstraction.

Provides VLAN ID validation, Priority Code Point (PCP) handling,
Drop Eligible Indicator (DEI) flags, and 4-byte 802.1Q header serialization/parsing.
"""

from lablink.exceptions import InvalidVLANError


class VLANHeader:
    """
    IEEE 802.1Q VLAN Tag Header (4 bytes).
    """

    TPID_8021Q: int = 0x8100

    def __init__(
        self,
        vlan_id: int,
        pcp: int = 0,
        dei: bool = False,
        tpid: int = TPID_8021Q,
    ) -> None:
        if not (0 <= vlan_id <= 4095):
            raise InvalidVLANError(f"VLAN ID must be in range 0..4095, got {vlan_id}")
        if not (0 <= pcp <= 7):
            raise InvalidVLANError(f"PCP priority must be in range 0..7, got {pcp}")

        self.vlan_id: int = vlan_id
        self.pcp: int = pcp
        self.dei: bool = dei
        self.tpid: int = tpid

    def to_bytes(self) -> bytes:
        """
        Serialize 802.1Q VLAN tag header into 4 bytes.

        Bytes 0..1: TPID (0x8100)
        Bytes 2..3: TCI (3 bits PCP | 1 bit DEI | 12 bits VLAN ID)
        """
        tci = ((self.pcp & 0x07) << 13) | ((1 if self.dei else 0) << 12) | (self.vlan_id & 0x0FFF)
        return self.tpid.to_bytes(2, "big") + tci.to_bytes(2, "big")

    @classmethod
    def parse(cls, data: bytes) -> tuple["VLANHeader", bytes]:
        """
        Parse 4-byte 802.1Q VLAN tag from raw byte stream.

        Returns:
            Tuple of (VLANHeader instance, remaining_payload_bytes).
        """
        if len(data) < 4:
            raise InvalidVLANError(
                f"VLAN header data truncated: expected >= 4 bytes, got {len(data)}"
            )

        tpid = int.from_bytes(data[0:2], "big")
        tci = int.from_bytes(data[2:4], "big")

        pcp = (tci >> 13) & 0x07
        dei = bool((tci >> 12) & 0x01)
        vlan_id = tci & 0x0FFF

        header = cls(vlan_id=vlan_id, pcp=pcp, dei=dei, tpid=tpid)
        return header, data[4:]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VLANHeader):
            return (
                self.vlan_id == other.vlan_id
                and self.pcp == other.pcp
                and self.dei == other.dei
                and self.tpid == other.tpid
            )
        return False

    def __repr__(self) -> str:
        return f"VLANHeader(vlan_id={self.vlan_id}, pcp={self.pcp}, dei={self.dei})"
