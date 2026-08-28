"""
Functional tests for manufacturing simulation engine, yield analytics, and reporting.
"""

import pytest

from lablink.manufacturing.analytics import YieldAnalytics
from lablink.manufacturing.reporting import ManufacturingReporter
from lablink.manufacturing.simulation import ManufacturingSimulationEngine


@pytest.mark.manufacturing
def test_manufacturing_simulation_yield_analytics_calculation() -> None:
    engine = ManufacturingSimulationEngine(seed=42)
    results = engine.run_simulation(num_duts=50, fail_rate=0.20, retest_failed=True)

    assert len(results) > 50  # First pass runs + retests

    metrics = YieldAnalytics.calculate_yield(results)
    assert metrics.total_units_tested == 50
    assert 0.0 <= metrics.first_pass_yield_percentage <= 100.0
    assert 0.0 <= metrics.final_yield_percentage <= 100.0
    assert metrics.final_yield_percentage >= metrics.first_pass_yield_percentage


@pytest.mark.manufacturing
def test_manufacturing_reporter_exports() -> None:
    engine = ManufacturingSimulationEngine(seed=100)
    results = engine.run_simulation(num_duts=10, fail_rate=0.10)

    json_report = ManufacturingReporter.export_json(results)
    assert '"total_duts": 10' in json_report

    csv_report = ManufacturingReporter.export_csv(results)
    assert "DUT_Serial,Sequence_Name" in csv_report
    assert "SN-OPT-MODULE-0001" in csv_report
