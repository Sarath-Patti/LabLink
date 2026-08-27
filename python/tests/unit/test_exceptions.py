"""
Unit tests for LabLink exception hierarchy and error model.
"""

from lablink.exceptions import (
    DisconnectedTransportError,
    InvalidResponseError,
    LabLinkError,
    ProtocolError,
    SCPIError,
    TransportConnectionError,
    TransportError,
    TransportIOError,
    TransportTimeoutError,
    VISAError,
)


def test_exception_inheritance() -> None:
    """Verify inheritance relationships across the exception hierarchy."""
    assert issubclass(TransportError, LabLinkError)
    assert issubclass(TransportConnectionError, TransportError)
    assert issubclass(TransportTimeoutError, TransportError)
    assert issubclass(TransportIOError, TransportError)
    assert issubclass(DisconnectedTransportError, TransportError)

    assert issubclass(ProtocolError, LabLinkError)
    assert issubclass(SCPIError, ProtocolError)
    assert issubclass(InvalidResponseError, ProtocolError)
    assert issubclass(VISAError, ProtocolError)


def test_scpi_error_attributes() -> None:
    """Verify SCPIError preserves numeric code and message attributes."""
    err = SCPIError(-113, "Undefined header")
    assert err.code == -113
    assert err.message == "Undefined header"
    assert "SCPI Error [-113]: Undefined header" in str(err)
