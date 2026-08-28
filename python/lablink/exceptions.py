"""
LabLink Unified Exception Hierarchy.

Provides structured, domain-specific exception types across transport,
protocol, instrument, network, and system modules.
"""


class LabLinkError(Exception):
    """Base exception for all LabLink errors."""


# =====================================================================
# Transport Layer Exceptions
# =====================================================================


class TransportError(LabLinkError):
    """Base exception for transport communication failures."""


class TransportConnectionError(TransportError):
    """Raised when a connection to a remote host or serial port fails."""


class TransportTimeoutError(TransportError):
    """Raised when a transport read, write, or connect operation times out."""


class TransportIOError(TransportError):
    """Raised when an I/O stream error occurs during read or write operations."""


class DisconnectedTransportError(TransportError):
    """Raised when an operation is attempted on a disconnected transport."""


# =====================================================================
# Protocol & VISA Exceptions
# =====================================================================


class ProtocolError(LabLinkError):
    """Base exception for protocol framing, parsing, or command errors."""


class SCPIError(ProtocolError):
    """Raised when a SCPI command error or status query failure occurs."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"SCPI Error [{code}]: {message}")


class InvalidResponseError(ProtocolError):
    """Raised when an unexpected or malformed response is received."""


class VISAError(ProtocolError):
    """Raised when a VISA resource addressing or configuration error occurs."""


# =====================================================================
# Network & Layer-2 Exceptions
# =====================================================================


class NetworkError(ProtocolError):
    """Base exception for network framing, MAC address, or Layer-2 errors."""


class InvalidMACAddressError(NetworkError):
    """Raised when a MAC address string or byte array is invalid."""


class InvalidVLANError(NetworkError):
    """Raised when a 802.1Q VLAN ID or priority parameter is out of range."""


class MalformedFrameError(NetworkError):
    """Raised when an Ethernet frame byte sequence is truncated or corrupt."""
