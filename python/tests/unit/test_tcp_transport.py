"""
Unit tests for TCPTransport socket operations, timeout handling, and errors.
"""

from unittest.mock import MagicMock, patch

import pytest

from lablink.exceptions import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeoutError,
)
from lablink.transport.tcp import TCPTransport


def test_tcp_transport_initialization() -> None:
    """Verify default initialization parameters."""
    transport = TCPTransport(host="192.168.1.50", port=5025, timeout=2.5)
    assert transport.host == "192.168.1.50"
    assert transport.port == 5025
    assert transport.timeout == 2.5
    assert not transport.is_connected


@patch("socket.socket")
def test_tcp_connect_success(mock_socket_cls: MagicMock) -> None:
    """Verify successful TCP connection setup."""
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport(host="127.0.0.1", port=5025)
    transport.connect()

    assert transport.is_connected
    mock_sock.settimeout.assert_called_with(5.0)
    mock_sock.connect.assert_called_with(("127.0.0.1", 5025))


@patch("socket.socket")
def test_tcp_connect_timeout(mock_socket_cls: MagicMock) -> None:
    """Verify socket timeout during connect raises TransportTimeoutError."""
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = TimeoutError("Connect timed out")
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport(host="10.0.0.1", port=5025)
    with pytest.raises(TransportTimeoutError, match="timed out"):
        transport.connect()

    assert not transport.is_connected


@patch("socket.socket")
def test_tcp_connect_refused(mock_socket_cls: MagicMock) -> None:
    """Verify connection refused raises TransportConnectionError."""
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = OSError("Connection refused")
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport(host="127.0.0.1", port=9999)
    with pytest.raises(TransportConnectionError, match="Failed to connect"):
        transport.connect()

    assert not transport.is_connected


@patch("socket.socket")
def test_tcp_write_and_read_success(mock_socket_cls: MagicMock) -> None:
    """Verify write and read payloads over connected socket."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"*IDN? Response\n"
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport()
    transport.connect()

    written = transport.write("*IDN?\n")
    assert written == 6
    mock_sock.sendall.assert_called_with(b"*IDN?\n")

    response = transport.read(1024)
    assert response == b"*IDN? Response\n"


@patch("socket.socket")
def test_tcp_read_peer_closed(mock_socket_cls: MagicMock) -> None:
    """Verify receiving b'' indicates remote connection closure."""
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b""
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport()
    transport.connect()

    with pytest.raises(TransportIOError, match="closed by remote host"):
        transport.read()

    assert not transport.is_connected


@patch("socket.socket")
def test_tcp_disconnect(mock_socket_cls: MagicMock) -> None:
    """Verify clean socket disconnect."""
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock

    transport = TCPTransport()
    transport.connect()
    assert transport.is_connected

    transport.disconnect()
    assert not transport.is_connected
    mock_sock.close.assert_called_once()
