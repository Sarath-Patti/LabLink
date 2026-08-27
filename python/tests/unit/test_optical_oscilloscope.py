"""
Unit tests for OpticalOscilloscope instrument control.
"""

import pytest

from lablink.instruments.optical_oscilloscope import OpticalOscilloscope, WaveformData
from lablink.transport.mock import MockTransport


def test_optical_oscilloscope_configuration() -> None:
    """Verify timebase scale, channel scale, and acquisition state control."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("TIMEBASE:SCALE?\n", "0.001\n")
    mock_transport.add_response("CHANNEL:SCALE?\n", "0.5\n")
    mock_transport.add_response("ACQUIRE:STATE?\n", "1\n")

    scope = OpticalOscilloscope(transport=mock_transport)

    scope.set_timebase_scale(1e-3)
    assert mock_transport.written_history[-1] == b"TIMEBASE:SCALE 0.001\n"
    assert scope.get_timebase_scale() == 1e-3

    scope.set_channel_scale(0.5)
    assert mock_transport.written_history[-1] == b"CHANNEL:SCALE 0.5\n"
    assert scope.get_channel_scale() == 0.5

    scope.set_acquisition_state(True)
    assert mock_transport.written_history[-1] == b"ACQUIRE:STATE ON\n"
    assert scope.get_acquisition_state() is True

    with pytest.raises(ValueError, match="must be positive"):
        scope.set_timebase_scale(-1.0)


def test_optical_oscilloscope_waveform_acquisition() -> None:
    """Verify acquiring structured waveform sample data."""
    mock_transport = MockTransport(auto_connect=True)
    mock_transport.add_response("TIMEBASE:SCALE?\n", "0.001\n")
    mock_transport.add_response("CHANNEL:SCALE?\n", "0.5\n")
    mock_transport.add_response("WAVEFORM:DATA?\n", "0.0,0.25,0.5,0.25,0.0,-0.25,-0.5\n")

    scope = OpticalOscilloscope(transport=mock_transport)
    wf = scope.acquire_waveform()

    assert isinstance(wf, WaveformData)
    assert wf.time_scale == 1e-3
    assert wf.voltage_scale == 0.5
    assert len(wf.samples) == 7
    assert wf.samples[2] == 0.5
