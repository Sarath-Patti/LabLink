"""
Unit tests for OpticalSwitch instrument control.
"""

import pytest

from lablink.instruments.optical_switch import OpticalSwitch
from lablink.transport.mock import MockTransport


def test_optical_switch_routing() -> None:
    """Verify route configuration, route query, and channel count."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("ROUTE?\n", "3\n")
    mock_transport.add_response("ROUTE:CHAN:COUNT?\n", "8\n")

    sw = OpticalSwitch(transport=mock_transport)

    sw.set_route(3)
    assert mock_transport.written_history[-1] == b"ROUTE:SET 3\n"

    assert sw.get_route() == 3
    assert sw.get_channel_count() == 8

    with pytest.raises(ValueError, match="must be >= 1"):
        sw.set_route(0)
