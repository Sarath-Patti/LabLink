"""
Performance Test Suite — SCPI Query Latency and Measurement Throughput Benchmarks.

Collects empirical round-trip timing measurements for SCPI queries and instrument operations
against localhost TCP simulators using conservative thresholds.
"""

import pytest

from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from tests.utilities.assertions import assert_less_than
from tests.utilities.helpers import measure_execution_time
from tests.utilities.reporting import JSONResultExporter, TestMeasurementResult


@pytest.mark.performance
def test_scpi_query_latency_performance(opm_client: OpticalPowerMeter) -> None:
    """
    Measure SCPI query round-trip latency over multiple iterations.
    """
    exporter = JSONResultExporter("performance_results.json")
    iterations = 30
    durations_ms: list[float] = []

    for i in range(iterations):
        _, duration = measure_execution_time(opm_client.identify)
        durations_ms.append(duration * 1000.0)

    avg_latency_ms = sum(durations_ms) / iterations

    exporter.record_result(
        TestMeasurementResult(
            test_name="scpi_query_latency_performance",
            category="performance",
            status="PASS",
            duration_ms=avg_latency_ms,
            instrument="OpticalPowerMeter",
            measurement_name="avg_scpi_query_latency",
            expected=50.0,
            actual=avg_latency_ms,
            unit="ms",
        )
    )

    # Assert conservative upper bound threshold (average latency < 50ms over localhost)
    assert_less_than(avg_latency_ms, 50.0, "Average SCPI query latency exceeded threshold")
    exporter.export()


@pytest.mark.performance
def test_power_measurement_throughput_performance(
    opm_client: OpticalPowerMeter,
) -> None:
    """
    Measure optical power measurement throughput over multiple iterations.
    """
    iterations = 20
    durations_ms: list[float] = []

    for _ in range(iterations):
        _, duration = measure_execution_time(opm_client.measure_power)
        durations_ms.append(duration * 1000.0)

    avg_measurement_duration_ms = sum(durations_ms) / iterations
    assert_less_than(
        avg_measurement_duration_ms, 50.0, "Average measurement duration exceeded threshold"
    )


@pytest.mark.performance
def test_optical_switch_route_latency_performance(
    switch_client: OpticalSwitch,
) -> None:
    """
    Measure optical switch route command latency.
    """
    durations_ms: list[float] = []

    for channel in [1, 2, 3, 4, 1]:
        _, duration = measure_execution_time(switch_client.set_route, channel)
        durations_ms.append(duration * 1000.0)

    avg_switch_duration_ms = sum(durations_ms) / len(durations_ms)
    assert_less_than(
        avg_switch_duration_ms, 50.0, "Average switch route latency exceeded threshold"
    )
