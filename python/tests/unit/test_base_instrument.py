"""
Unit tests for BaseInstrument abstraction.
"""

import pytest

from lablink.exceptions import SCPIError
from lablink.instruments.base import BaseInstrument
from lablink.transport.mock import MockTransport


class ConcreteInstrument(BaseInstrument):
    """Concrete subclass of BaseInstrument for testing."""


def test_base_instrument_connection_and_timeout() -> None:
    """Verify base instrument connection and timeout properties delegation."""
    mock_transport = MockTransport()
    inst = ConcreteInstrument(transport=mock_transport)

    assert not inst.is_connected
    inst.connect()
    assert inst.is_connected

    inst.timeout = 4.5
    assert inst.timeout == 4.5

    inst.disconnect()
    assert not inst.is_connected


def test_base_instrument_scpi_delegation() -> None:
    """Verify write, read, query, identify, reset, clear, and system error check."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("*IDN?\n", "LabLink,TestModel,SN123,v1.0\n")
    mock_transport.add_response("SYST:ERR?\n", '+0,"No error"\n')

    inst = ConcreteInstrument(transport=mock_transport)

    assert inst.identify() == "LabLink,TestModel,SN123,v1.0"

    inst.reset()
    assert mock_transport.written_history[-1] == b"*RST\n"

    inst.clear()
    assert mock_transport.written_history[-1] == b"*CLS\n"

    code, msg = inst.get_system_error()
    assert code == 0
    assert msg == "No error"

    inst.check_system_errors()


def test_base_instrument_system_error_raises() -> None:
    """Verify check_system_errors raises SCPIError when code != 0."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("SYST:ERR?\n", '-113,"Undefined header"\n')

    inst = ConcreteInstrument(transport=mock_transport)
    with pytest.raises(SCPIError, match="Undefined header"):
        inst.check_system_errors()
