"""
Unit tests for NetworkSwitch device port control.
"""

import pytest

from lablink.devices.network_switch import NetworkSwitch
from lablink.transport.mock import MockTransport


def test_network_switch_port_control() -> None:
    """Verify port count, enable/disable port, get_port_state, and get_all_port_states."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("PORT:COUNT?\n", "24\n")
    mock_transport.add_response("PORT:STATE? 1\n", "1\n")
    mock_transport.add_response("PORT:STATE? 2\n", "0\n")
    mock_transport.add_response("PORT:ALL?\n", "1:UP,2:DOWN,3:UP\n")

    switch = NetworkSwitch(transport=mock_transport)

    assert switch.get_port_count() == 24

    switch.enable_port(1)
    assert mock_transport.written_history[-1] == b"PORT:ENABLE 1\n"
    assert switch.get_port_state(1) is True

    switch.disable_port(2)
    assert mock_transport.written_history[-1] == b"PORT:DISABLE 2\n"
    assert switch.get_port_state(2) is False

    all_states = switch.get_all_port_states()
    assert all_states == {1: True, 2: False, 3: True}

    with pytest.raises(ValueError, match="must be >= 1"):
        switch.enable_port(0)
