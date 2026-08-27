"""
Functional test suite for NetworkSwitch device control operations.
"""

import pytest

from lablink.devices.network_switch import NetworkSwitch


@pytest.mark.functional
@pytest.mark.instrument
def test_network_switch_identification(net_switch_client: NetworkSwitch) -> None:
    """Verify NetworkSwitch device identification query."""
    idn = net_switch_client.identify()
    assert "Nexus-9000-Sim" in idn


@pytest.mark.functional
@pytest.mark.instrument
def test_network_switch_port_capacity(net_switch_client: NetworkSwitch) -> None:
    """Verify NetworkSwitch port count query."""
    assert net_switch_client.get_port_count() == 24


@pytest.mark.functional
@pytest.mark.instrument
def test_network_switch_port_state_control(net_switch_client: NetworkSwitch) -> None:
    """Verify enabling, disabling, and querying specific port states."""
    assert net_switch_client.get_port_state(1) is True

    net_switch_client.disable_port(1)
    assert net_switch_client.get_port_state(1) is False

    net_switch_client.enable_port(1)
    assert net_switch_client.get_port_state(1) is True


@pytest.mark.functional
@pytest.mark.instrument
def test_network_switch_all_port_states(net_switch_client: NetworkSwitch) -> None:
    """Verify retrieving full administrative port state table."""
    states = net_switch_client.get_all_port_states()
    assert len(states) == 24
    assert all(state is True for state in states.values())
