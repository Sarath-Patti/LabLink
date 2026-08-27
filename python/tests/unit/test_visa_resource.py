"""
Unit tests for VISAResource and VISAResourceManager descriptor parsing.
"""

import pytest

from lablink.exceptions import VISAError
from lablink.protocols.visa import VISAResource, VISAResourceManager
from lablink.transport.mock import MockTransport
from lablink.transport.serial import SerialTransport
from lablink.transport.tcp import TCPTransport


def test_visa_manager_tcp_descriptor_parsing() -> None:
    """Verify parsing TCPIP descriptors into TCPTransport resources without connecting."""
    res = VISAResourceManager.get_resource("TCPIP0::192.168.1.100::5025::SOCKET", timeout=3.0)
    assert isinstance(res, VISAResource)
    assert isinstance(res.transport, TCPTransport)
    assert res.transport.host == "192.168.1.100"
    assert res.transport.port == 5025
    assert res.timeout == 3.0
    assert not res.is_connected


def test_visa_manager_serial_descriptor_parsing() -> None:
    """Verify parsing ASRL descriptors into SerialTransport resources."""
    res = VISAResourceManager.get_resource("ASRL1::9600::INSTR")
    assert isinstance(res, VISAResource)
    assert isinstance(res.transport, SerialTransport)
    assert res.transport.baudrate == 9600
    assert not res.is_connected


def test_visa_manager_mock_descriptor_parsing() -> None:
    """Verify parsing MOCK descriptors into MockTransport resources."""
    res = VISAResourceManager.open_resource("MOCK::SIMULATOR::INSTR")
    try:
        assert isinstance(res, VISAResource)
        assert isinstance(res.transport, MockTransport)
        assert res.is_connected
    finally:
        res.close()


def test_visa_manager_invalid_descriptor_raises() -> None:
    """Verify malformed VISA descriptor raises VISAError."""
    with pytest.raises(VISAError, match="Unsupported or malformed"):
        VISAResourceManager.open_resource("INVALID_VISA_DESCRIPTOR_STRING")


def test_visa_resource_operations() -> None:
    """Verify write, read, query, clear operations on VISAResource."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("*IDN?\n", "RIGOL,DS1054Z,DS1A123456789,00.04.04\n")

    res = VISAResource("MOCK::TEST::INSTR", transport=mock_transport)
    assert res.is_connected

    resp = res.query("*IDN?")
    assert resp == "RIGOL,DS1054Z,DS1A123456789,00.04.04"

    res.clear()
    assert mock_transport.written_history[-1] == b"*CLS\n"
