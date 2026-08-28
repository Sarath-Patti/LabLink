"""
Test Step Executor & Measurement Ingestion.

Executes ordered test steps against DUT and instruments, handles retries/timeouts, evaluates limits, and records measurements.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lablink.exceptions import TransportConnectionError, TransportTimeoutError
from lablink.manufacturing.dut import DUT
from lablink.manufacturing.limits import LimitEvaluator
from lablink.manufacturing.sequence import TestSequence, TestStep
from lablink.manufacturing.verdict import FailureCode, Verdict, VerdictEngine


@dataclass
class RecordedMeasurement:
    step_name: str
    measurement_name: str
    value: Any
    unit: str
    passed: bool
    lower_limit: float | None = None
    upper_limit: float | None = None
    expected_value: Any | None = None
    verdict: Verdict = Verdict.PASS
    failure_code: FailureCode = FailureCode.NONE
    instrument_source: str = "Simulator"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: str | None = None


@dataclass
class StepExecutionResult:
    step_name: str
    verdict: Verdict
    failure_code: FailureCode
    measurements: list[RecordedMeasurement]
    duration_seconds: float
    error_message: str | None = None


@dataclass
class ManufacturingExecutionResult:
    dut_serial: str
    sequence_name: str
    sequence_version: str
    station_id: str
    software_version: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    overall_verdict: Verdict
    failure_code: FailureCode
    step_results: list[StepExecutionResult]
    all_measurements: list[RecordedMeasurement]
    failure_summary: str | None = None


class TestExecutor:
    __test__ = False  # Prevent pytest from treating domain class as a test suite

    def __init__(
        self,
        station_id: str = "Station-01",
        software_version: str = "1.0.0",
        fail_fast: bool = False,
    ) -> None:
        self.station_id = station_id
        self.software_version = software_version
        self.fail_fast = fail_fast

    def execute_sequence(
        self,
        dut: DUT,
        sequence: TestSequence,
        context: dict[str, Any] | None = None,
    ) -> ManufacturingExecutionResult:
        context = context or {}
        started_at = datetime.utcnow()  # noqa: DTZ003

        step_results: list[StepExecutionResult] = []
        all_measurements: list[RecordedMeasurement] = []
        overall_failure_code = FailureCode.NONE
        failure_summaries: list[str] = []

        for step in sequence.get_enabled_steps():
            step_result = self._execute_step(dut, step, context)
            step_results.append(step_result)
            all_measurements.extend(step_result.measurements)

            if step_result.verdict in (Verdict.FAIL, Verdict.ERROR):
                if overall_failure_code == FailureCode.NONE:
                    overall_failure_code = step_result.failure_code
                if step_result.error_message:
                    failure_summaries.append(f"{step.name}: {step_result.error_message}")

                if self.fail_fast and step.critical:
                    break

        completed_at = datetime.utcnow()  # noqa: DTZ003
        duration_sec = round((completed_at - started_at).total_seconds(), 3)
        overall_verdict = VerdictEngine.calculate_overall_verdict(
            [sr.verdict for sr in step_results]
        )

        return ManufacturingExecutionResult(
            dut_serial=dut.serial_number,
            sequence_name=sequence.name,
            sequence_version=sequence.version,
            station_id=self.station_id,
            software_version=self.software_version,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_sec,
            overall_verdict=overall_verdict,
            failure_code=(
                overall_failure_code if overall_verdict != Verdict.PASS else FailureCode.NONE
            ),
            step_results=step_results,
            all_measurements=all_measurements,
            failure_summary=" | ".join(failure_summaries) if failure_summaries else None,
        )

    def _execute_step(
        self,
        dut: DUT,
        step: TestStep,
        context: dict[str, Any],
    ) -> StepExecutionResult:
        step_start = datetime.utcnow()  # noqa: DTZ003
        attempts = 0
        max_attempts = max(1, step.max_retries + 1)

        step_verdict = Verdict.ERROR
        step_failure_code = FailureCode.SOFTWARE_ERROR
        step_measurements: list[RecordedMeasurement] = []
        step_err: str | None = None

        while attempts < max_attempts:
            attempts += 1
            step_measurements = []
            try:
                raw_output = step.action(dut, context)

                # Process returned measurement dictionary or list
                if isinstance(raw_output, dict):
                    raw_measurements = [raw_output]
                elif isinstance(raw_output, list):
                    raw_measurements = raw_output
                else:
                    raw_measurements = [{"value": raw_output, "name": step.identifier}]

                step_failed = False
                for limit in step.limits:
                    # Match raw measurement value by limit name or default
                    matched_raw = next(
                        (m for m in raw_measurements if m.get("name") == limit.measurement_name),
                        raw_measurements[0] if raw_measurements else {"value": None},
                    )

                    eval_res = LimitEvaluator.evaluate(limit, matched_raw.get("value"))
                    m_verdict = Verdict.PASS if eval_res.passed else Verdict.FAIL
                    m_fail_code = (
                        FailureCode.NONE
                        if eval_res.passed
                        else FailureCode.MEASUREMENT_OUT_OF_LIMIT
                    )

                    if not eval_res.passed:
                        step_failed = True

                    source_name = str(matched_raw.get("source") or "InstrumentSimulator")

                    rec = RecordedMeasurement(
                        step_name=step.name,
                        measurement_name=limit.measurement_name,
                        value=eval_res.value,
                        unit=limit.unit,
                        passed=eval_res.passed,
                        lower_limit=limit.lower_limit,
                        upper_limit=limit.upper_limit,
                        expected_value=eval_res.expected_value,
                        verdict=m_verdict,
                        failure_code=m_fail_code,
                        instrument_source=source_name,
                        error_message=eval_res.error_message,
                    )
                    step_measurements.append(rec)

                if step_failed:
                    step_verdict = Verdict.FAIL
                    step_failure_code = FailureCode.MEASUREMENT_OUT_OF_LIMIT
                    step_err = "One or more measurements exceeded configured limits."
                else:
                    step_verdict = Verdict.PASS
                    step_failure_code = FailureCode.NONE
                    step_err = None
                    break  # Success, exit retry loop

            except TransportConnectionError as e:
                step_verdict = Verdict.ERROR
                step_failure_code = FailureCode.INSTRUMENT_CONNECTION
                step_err = f"Instrument Connection Error: {e}"
            except TransportTimeoutError as e:
                step_verdict = Verdict.ERROR
                step_failure_code = FailureCode.INSTRUMENT_TIMEOUT
                step_err = f"Instrument Timeout Error: {e}"
            except TimeoutError as e:
                step_verdict = Verdict.ERROR
                step_failure_code = FailureCode.TEST_TIMEOUT
                step_err = f"Test Timeout Error: {e}"
            except Exception as e:  # noqa: BLE001
                step_verdict = Verdict.ERROR
                step_failure_code = FailureCode.SOFTWARE_ERROR
                step_err = f"Execution Error: {e}"

        step_end = datetime.utcnow()  # noqa: DTZ003
        duration_sec = round((step_end - step_start).total_seconds(), 3)

        return StepExecutionResult(
            step_name=step.name,
            verdict=step_verdict,
            failure_code=step_failure_code,
            measurements=step_measurements,
            duration_seconds=duration_sec,
            error_message=step_err,
        )
