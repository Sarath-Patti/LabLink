"""
Unit tests for SCPIProtocol command formatting, IEEE 488.2 commands, and response parsers.
"""

import pytest

from lablink.exceptions import InvalidResponseError, SCPIError
from lablink.protocols.scpi import SCPIProtocol
from lablink.transport.mock import MockTransport


def test_scpi_command_formatting_and_query() -> None:
    """Verify SCPI write and query command termination formatting."""
    mock = MockTransport(auto_connect=True)
    scpi = SCPIProtocol(transport=mock, read_termination="\n", write_termination="\n")

    mock.add_response("*IDN?\n", "AGILENT,34401A,MY12345678,1.0-1.0\n")

    idn_resp = scpi.query("*IDN?")
    assert idn_resp == "AGILENT,34401A,MY12345678,1.0-1.0"
    assert mock.written_history == [b"*IDN?\n"]


def test_scpi_ieee_488_2_common_commands() -> None:
    """Verify IEEE 488.2 common commands (*IDN?, *RST, *CLS, SYST:ERR?)."""
    mock = MockTransport(auto_connect=True)
    scpi = SCPIProtocol(transport=mock)

    mock.add_response("SYST:ERR?\n", '+0,"No error"\n')

    scpi.reset()
    assert mock.written_history[-1] == b"*RST\n"

    scpi.clear()
    assert mock.written_history[-1] == b"*CLS\n"

    code, msg = scpi.get_system_error()
    assert code == 0
    assert msg == "No error"


def test_scpi_error_checking_raises() -> None:
    """Verify check_system_errors raises SCPIError for non-zero error codes."""
    mock = MockTransport(auto_connect=True)
    scpi = SCPIProtocol(transport=mock)

    mock.add_response("SYST:ERR?\n", '-113,"Undefined header"\n')

    with pytest.raises(SCPIError) as exc_info:
        scpi.check_system_errors()

    assert exc_info.value.code == -113
    assert exc_info.value.message == "Undefined header"


def test_scpi_response_parsers() -> None:
    """Verify response parsing helpers (numeric, comma-separated, boolean)."""
    assert SCPIProtocol.parse_numeric(" 12.345 \n") == 12.345
    assert SCPIProtocol.parse_comma_separated("HP, 54600B, 0, 1.2") == ["HP", "54600B", "0", "1.2"]

    assert SCPIProtocol.parse_boolean("1") is True
    assert SCPIProtocol.parse_boolean("ON") is True
    assert SCPIProtocol.parse_boolean("0") is False
    assert SCPIProtocol.parse_boolean("OFF") is False

    with pytest.raises(InvalidResponseError):
        SCPIProtocol.parse_numeric("INVALID_FLOAT")

    with pytest.raises(InvalidResponseError):
        SCPIProtocol.parse_boolean("UNKNOWN")
