"""
Manufacturing Reporter.

Generates structured JSON, CSV, and summary reports from persisted manufacturing test data.
"""

import csv
import io
import json
from typing import Any

from lablink.manufacturing.analytics import YieldAnalytics, YieldMetrics
from lablink.manufacturing.executor import ManufacturingExecutionResult


class ManufacturingReporter:
    @staticmethod
    def generate_summary_report(
        results: list[ManufacturingExecutionResult],
    ) -> dict[str, Any]:
        metrics: YieldMetrics = YieldAnalytics.calculate_yield(results)
        return {
            "summary": {
                "total_runs": len(results),
                "total_duts": metrics.total_units_tested,
                "first_pass_yield_pct": metrics.first_pass_yield_percentage,
                "final_yield_pct": metrics.final_yield_percentage,
            },
            "analytics": {
                "failures_by_step": metrics.failures_by_step,
                "failures_by_code": metrics.failures_by_code,
                "failures_by_station": metrics.failures_by_station,
                "failures_by_version": metrics.failures_by_version,
            },
            "recent_runs": [
                {
                    "dut_serial": r.dut_serial,
                    "sequence": r.sequence_name,
                    "version": r.sequence_version,
                    "station": r.station_id,
                    "verdict": r.overall_verdict.value,
                    "duration_sec": r.duration_seconds,
                    "failure_code": r.failure_code.value,
                }
                for r in results[-10:]
            ],
        }

    @staticmethod
    def export_json(results: list[ManufacturingExecutionResult]) -> str:
        report = ManufacturingReporter.generate_summary_report(results)
        return json.dumps(report, indent=2)

    @staticmethod
    def export_csv(results: list[ManufacturingExecutionResult]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "DUT_Serial",
                "Sequence_Name",
                "Sequence_Version",
                "Station_ID",
                "Software_Version",
                "Started_At",
                "Completed_At",
                "Duration_Sec",
                "Overall_Verdict",
                "Failure_Code",
                "Failure_Summary",
            ]
        )

        for r in results:
            writer.writerow(
                [
                    r.dut_serial,
                    r.sequence_name,
                    r.sequence_version,
                    r.station_id,
                    r.software_version,
                    r.started_at.isoformat(),
                    r.completed_at.isoformat(),
                    r.duration_seconds,
                    r.overall_verdict.value,
                    r.failure_code.value,
                    r.failure_summary or "",
                ]
            )

        return output.getvalue()
