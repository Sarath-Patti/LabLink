"""
High-Volume Manufacturing Simulation Performance Benchmark.

Benchmarks seed-controlled simulation execution for 100+ to 500+ DUTs.
"""

import time

import pytest

from lablink.manufacturing.analytics import YieldAnalytics
from lablink.manufacturing.simulation import ManufacturingSimulationEngine


@pytest.mark.performance
@pytest.mark.manufacturing
def test_high_volume_manufacturing_simulation_100_duts_benchmark() -> None:
    engine = ManufacturingSimulationEngine(seed=42)

    start = time.perf_counter()
    results = engine.run_simulation(num_duts=100, fail_rate=0.15)
    end = time.perf_counter()

    duration_sec = round(end - start, 3)
    avg_per_run_ms = round((duration_sec / len(results)) * 1000.0, 2)

    metrics = YieldAnalytics.calculate_yield(results)

    assert metrics.total_units_tested == 100
    assert len(results) >= 100
    assert duration_sec < 5.0  # Must execute under 5 seconds locally

    print(
        f"\n[BENCHMARK] 100 DUT Simulation: {len(results)} runs in {duration_sec}s ({avg_per_run_ms}ms/run). FPY: {metrics.first_pass_yield_percentage}%"
    )


@pytest.mark.performance
@pytest.mark.manufacturing
def test_high_volume_manufacturing_simulation_500_duts_benchmark() -> None:
    engine = ManufacturingSimulationEngine(seed=42)

    start = time.perf_counter()
    results = engine.run_simulation(num_duts=500, fail_rate=0.15)
    end = time.perf_counter()

    duration_sec = round(end - start, 3)
    avg_per_run_ms = round((duration_sec / len(results)) * 1000.0, 2)

    metrics = YieldAnalytics.calculate_yield(results)

    assert metrics.total_units_tested == 500
    assert len(results) >= 500
    assert duration_sec < 15.0  # Must execute under 15 seconds locally

    print(
        f"\n[BENCHMARK] 500 DUT Simulation: {len(results)} runs in {duration_sec}s ({avg_per_run_ms}ms/run). FPY: {metrics.first_pass_yield_percentage}%"
    )
