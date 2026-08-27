"""
Unit tests for MockTransport deterministic in-memory testing features.
"""

import pytest

from lablink.exceptions import (
    TransportConnectionError,
    TransportTimeoutError,
)
from lablink.transport.mock import MockTransport


def test_mock_transport_connect_and_disconnect() -> None:
    """Verify state transitions for connect and disconnect."""
    mock = MockTransport()
    assert not mock.is_connected

    mock.connect()
    assert mock.is_connected

    mock.disconnect()
    assert not mock.is_connected


def test_mock_transport_simulated_connection_failure() -> None:
    """Verify simulated connection failure when fail_connect is set."""
    mock = MockTransport()
    mock.fail_connect = True

    with pytest.raises(TransportConnectionError, match="Simulated connection failure"):
        mock.connect()

    assert not mock.is_connected


def test_mock_transport_write_history_and_responses() -> None:
    """Verify write history logging and automatic response pairing."""
    mock = MockTransport(auto_connect=True)
    mock.add_response("*IDN?\n", "KEYSIGHT,N5767A,US12345,1.0.0\n")

    written = mock.write("*IDN?\n")
    assert written == 6
    assert mock.written_history == [b"*IDN?\n"]

    response = mock.read()
    assert response == b"KEYSIGHT,N5767A,US12345,1.0.0\n"


def test_mock_transport_simulated_read_timeout() -> None:
    """Verify simulated read timeout exception."""
    mock = MockTransport(auto_connect=True)
    mock.fail_read_timeout = True

    with pytest.raises(TransportTimeoutError, match="Simulated read timeout"):
        mock.read()


def test_mock_transport_simulated_write_timeout() -> None:
    """Verify simulated write timeout exception."""
    mock = MockTransport(auto_connect=True)
    mock.fail_write_timeout = True

    with pytest.raises(TransportTimeoutError, match="Simulated write timeout"):
        mock.write("VOLT 5.0\n")


def test_mock_transport_custom_handler() -> None:
    """Verify dynamic custom response generator function."""
    mock = MockTransport(auto_connect=True)
    mock.set_custom_handler(lambda req: b"ECHO:" + req)

    resp = mock.query("PING")
    assert resp == b"ECHO:PING"
