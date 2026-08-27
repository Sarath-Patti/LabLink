"""
Functional test suite for OpticalSwitch instrument operations.
"""

import pytest

from lablink.instruments.optical_switch import OpticalSwitch


@pytest.mark.functional
@pytest.mark.instrument
def test_optical_switch_identification(switch_client: OpticalSwitch) -> None:
    """Verify OpticalSwitch identification query."""
    idn = switch_client.identify()
    assert "MAP-200-SW" in idn


@pytest.mark.functional
@pytest.mark.instrument
def test_optical_switch_channel_count(switch_client: OpticalSwitch) -> None:
    """Verify OpticalSwitch channel count query."""
    assert switch_client.get_channel_count() == 8


@pytest.mark.functional
@pytest.mark.instrument
@pytest.mark.parametrize("channel", [1, 2, 4, 8])
def test_optical_switch_routing_parameterized(switch_client: OpticalSwitch, channel: int) -> None:
    """Verify set_route and get_route across available switch channels."""
    switch_client.set_route(channel)
    assert switch_client.get_route() == channel


@pytest.mark.functional
@pytest.mark.instrument
def test_optical_switch_reset(switch_client: OpticalSwitch) -> None:
    """Verify reset restores optical switch active route to channel 1."""
    switch_client.set_route(5)
    assert switch_client.get_route() == 5
    switch_client.reset()
    assert switch_client.get_route() == 1
