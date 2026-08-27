"""
Functional test suite for OpticalOscilloscope instrument operations.
"""

import pytest

from lablink.instruments.optical_oscilloscope import OpticalOscilloscope, WaveformData
from tests.utilities.assertions import assert_within_tolerance


@pytest.mark.functional
@pytest.mark.instrument
def test_scope_identification(scope_client: OpticalOscilloscope) -> None:
    """Verify OpticalOscilloscope identification query."""
    idn = scope_client.identify()
    assert "MSO54-OPT" in idn


@pytest.mark.functional
@pytest.mark.instrument
@pytest.mark.parametrize("time_scale", [1e-4, 1e-3, 1e-2])
def test_scope_timebase_parameterized(scope_client: OpticalOscilloscope, time_scale: float) -> None:
    """Verify set_timebase_scale and get_timebase_scale across horizontal timebases."""
    scope_client.set_timebase_scale(time_scale)
    current_scale = scope_client.get_timebase_scale()
    assert_within_tolerance(current_scale, time_scale, 1e-6, "Timebase scale mismatch")


@pytest.mark.functional
@pytest.mark.instrument
def test_scope_channel_scale_and_acquisition(scope_client: OpticalOscilloscope) -> None:
    """Verify channel scale configuration and acquisition state control."""
    scope_client.set_channel_scale(0.25)
    assert_within_tolerance(scope_client.get_channel_scale(), 0.25, 0.001)

    scope_client.set_acquisition_state(True)
    assert scope_client.get_acquisition_state() is True


@pytest.mark.functional
@pytest.mark.instrument
def test_scope_waveform_acquisition(scope_client: OpticalOscilloscope) -> None:
    """Verify acquiring structured waveform sample data."""
    wf = scope_client.acquire_waveform()
    assert isinstance(wf, WaveformData)
    assert len(wf.samples) == 50
