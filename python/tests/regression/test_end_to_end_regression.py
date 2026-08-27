"""
Regression Test Suite — End-to-End Automated Optical Test Bench Workflow.

Executes complete multi-instrument test bench scenarios composing optical switches
and optical power meters to verify end-to-end regression stability.
"""

import pytest

from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from tests.utilities.assertions import assert_within_tolerance
from tests.utilities.reporting import JSONResultExporter, TestMeasurementResult


@pytest.mark.regression
def test_automated_optical_test_bench_regression(
    opm_client: OpticalPowerMeter, switch_client: OpticalSwitch
) -> None:
    """
    Verify complete multi-instrument optical test bench regression workflow:
    1. Identify all test instruments.
    2. Route optical matrix to target channel.
    3. Tune power meter wavelength.
    4. Measure optical power level.
    5. Verify zero SCPI errors across all instruments.
    """
    exporter = JSONResultExporter("test_results.json")

    # Step 1: Verify instrument identifications
    opm_idn = opm_client.identify()
    switch_idn = switch_client.identify()

    assert "N5767A-OPM" in opm_idn
    assert "MAP-200-SW" in switch_idn

    # Step 2: Test bench execution loop across multiple channels and wavelengths
    test_matrix = [
        (1, 1310.0, -10.0),
        (3, 1550.0, -10.0),
        (5, 1625.0, -10.0),
    ]

    for channel, wavelength, expected_power in test_matrix:
        switch_client.set_route(channel)
        assert switch_client.get_route() == channel

        opm_client.set_wavelength(wavelength)
        assert_within_tolerance(opm_client.get_wavelength(), wavelength, 0.01)

        measured_power = opm_client.measure_power()
        assert_within_tolerance(
            measured_power,
            expected_power,
            0.001,
            f"Power check failed at Ch{channel} @ {wavelength}nm",
        )

        exporter.record_result(
            TestMeasurementResult(
                test_name="automated_optical_test_bench_regression",
                category="regression",
                status="PASS",
                duration_ms=12.5,
                instrument="OpticalPowerMeter",
                measurement_name="optical_power",
                expected=expected_power,
                actual=measured_power,
                unit="dBm",
            )
        )

    # Step 3: Check system error queues to ensure clean execution
    opm_client.check_system_errors()
    switch_client.check_system_errors()

    # Step 4: Export telemetry
    report_path = exporter.export()
    assert report_path.is_file()
