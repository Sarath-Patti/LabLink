"""
Unit tests for SerialTransport configuration and virtual serial backend.
"""

from unittest.mock import MagicMock

from lablink.transport.serial import SerialTransport


def test_serial_transport_config() -> None:
    """Verify SerialTransport configuration properties."""
    transport = SerialTransport(
        port="COM3",
        baudrate=115200,
        bytesize=8,
        parity="E",
        stopbits=2.0,
        timeout=1.5,
    )

    assert transport.port == "COM3"
    assert transport.baudrate == 115200
    assert transport.bytesize == 8
    assert transport.parity == "E"
    assert transport.stopbits == 2.0
    assert transport.timeout == 1.5
    assert not transport.is_connected


def test_serial_with_virtual_backend() -> None:
    """Verify SerialTransport behavior using VirtualSerialBackend fallback."""
    transport = SerialTransport(port="COM1", baudrate=9600)
    transport.connect()
    assert transport.is_connected

    written = transport.write(b"*RST\n")
    assert written == 5

    transport.disconnect()
    assert not transport.is_connected


def test_serial_with_mock_backend() -> None:
    """Verify SerialTransport delegating to a custom mock backend."""
    mock_backend = MagicMock()
    mock_backend.is_open = True
    mock_backend.write.return_value = 10
    mock_backend.read.return_value = b"OK\n"

    transport = SerialTransport(port="/dev/ttyUSB0", backend=mock_backend)
    transport.connect()
    assert transport.is_connected

    written = transport.write("SYSTEM:OFF")
    assert written == 10
    mock_backend.write.assert_called_with(b"SYSTEM:OFF")

    data = transport.read()
    assert data == b"OK\n"
