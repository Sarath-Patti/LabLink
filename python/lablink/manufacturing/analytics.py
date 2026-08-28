"""
Yield Analytics Engine.

Calculates First Pass Yield (FPY), final yield after retest, failure breakdowns by step, failure code, station ID, and sequence version.
"""

from dataclasses import dataclass, field

from lablink.manufacturing.executor import ManufacturingExecutionResult
from lablink.manufacturing.verdict import FailureCode, Verdict


@dataclass
class YieldMetrics:
    total_units_tested: int
    first_pass_passed: int
    first_pass_yield_percentage: float
    final_passed: int
    final_yield_percentage: float
    failures_by_step: dict[str, int] = field(default_factory=dict)
    failures_by_code: dict[str, int] = field(default_factory=dict)
    failures_by_station: dict[str, int] = field(default_factory=dict)
    failures_by_version: dict[str, int] = field(default_factory=dict)


class YieldAnalytics:
    @staticmethod
    def calculate_yield(results: list[ManufacturingExecutionResult]) -> YieldMetrics:
        if not results:
            return YieldMetrics(
                total_units_tested=0,
                first_pass_passed=0,
                first_pass_yield_percentage=0.0,
                final_passed=0,
                final_yield_percentage=0.0,
            )

        # Group by DUT serial number
        dut_runs: dict[str, list[ManufacturingExecutionResult]] = {}
        for r in results:
            dut_runs.setdefault(r.dut_serial, []).append(r)

        total_units = len(dut_runs)
        first_pass_passed_count = 0
        final_passed_count = 0

        failures_step: dict[str, int] = {}
        failures_code: dict[str, int] = {}
        failures_station: dict[str, int] = {}
        failures_version: dict[str, int] = {}

        for runs in dut_runs.values():
            # Sort runs by started_at
            sorted_runs = sorted(runs, key=lambda x: x.started_at)
            first_run = sorted_runs[0]

            if first_run.overall_verdict == Verdict.PASS:
                first_pass_passed_count += 1

            if any(r.overall_verdict == Verdict.PASS for r in sorted_runs):
                final_passed_count += 1

            for run in sorted_runs:
                if run.overall_verdict != Verdict.PASS:
                    code_key = (
                        run.failure_code.value
                        if isinstance(run.failure_code, FailureCode)
                        else str(run.failure_code)
                    )
                    failures_code[code_key] = failures_code.get(code_key, 0) + 1

                    station_key = run.station_id or "Station-Unknown"
                    failures_station[station_key] = failures_station.get(station_key, 0) + 1

                    ver_key = run.sequence_version or "v1.0"
                    failures_version[ver_key] = failures_version.get(ver_key, 0) + 1

                    for step_res in run.step_results:
                        if step_res.verdict != Verdict.PASS:
                            step_key = step_res.step_name
                            failures_step[step_key] = failures_step.get(step_key, 0) + 1

        fpy = round((first_pass_passed_count / total_units) * 100.0, 2) if total_units > 0 else 0.0
        final_yield = (
            round((final_passed_count / total_units) * 100.0, 2) if total_units > 0 else 0.0
        )

        return YieldMetrics(
            total_units_tested=total_units,
            first_pass_passed=first_pass_passed_count,
            first_pass_yield_percentage=fpy,
            final_passed=final_passed_count,
            final_yield_percentage=final_yield,
            failures_by_step=failures_step,
            failures_by_code=failures_code,
            failures_by_station=failures_station,
            failures_by_version=failures_version,
        )
