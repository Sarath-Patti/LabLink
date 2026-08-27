"""
Unit tests for BaseTransport interface contract.
"""

import pytest

from lablink.exceptions import DisconnectedTransportError
from lablink.transport.base import BaseTransport


class ConcreteTransport(BaseTransport):
    """Minimal concrete implementation of BaseTransport for contract testing."""

    def __init__(self, timeout: float = 3.0) -> None:
        super().__init__(timeout=timeout)
        self.buffer = bytearray()

    def connect(self) -> None:
        self._is_connected = True

    def disconnect(self) -> None:
        self._is_connected = False

    def write(self, data: bytes | str) -> int:
        self._ensure_connected()
        payload = data.encode("utf-8") if isinstance(data, str) else data
        self.buffer.extend(payload)
        return len(payload)

    def read(self, size: int = 1024) -> bytes:
        self._ensure_connected()
        chunk = bytes(self.buffer[:size])
        del self.buffer[:size]
        return chunk


def test_base_transport_timeout_management() -> None:
    """Verify timeout getter and setter validation."""
    t = ConcreteTransport(timeout=4.5)
    assert t.timeout == 4.5

    t.timeout = 10.0
    assert t.timeout == 10.0

    with pytest.raises(ValueError, match="non-negative"):
        t.timeout = -1.0


def test_ensure_connected_raises() -> None:
    """Verify _ensure_connected raises DisconnectedTransportError when offline."""
    t = ConcreteTransport()
    assert not t.is_connected

    with pytest.raises(DisconnectedTransportError):
        t.write("test")

    with pytest.raises(DisconnectedTransportError):
        t.read()

    t.connect()
    assert t.is_connected
    t.write("hello")
    assert t.read() == b"hello"


def test_query_convenience_method() -> None:
    """Verify query performs write followed by read."""
    t = ConcreteTransport()
    t.connect()
    resp = t.query("PING")
    assert resp == b"PING"
