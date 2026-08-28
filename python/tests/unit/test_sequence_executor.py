"""
Unit tests for TestSequence and TestExecutor execution logic.
"""

from lablink.manufacturing.dut import DUT
from lablink.manufacturing.executor import TestExecutor
from lablink.manufacturing.limits import MeasurementLimit
from lablink.manufacturing.sequence import TestSequence, TestStep
from lablink.manufacturing.verdict import FailureCode, Verdict


def test_test_executor_passing_sequence() -> None:
    dut = DUT("SN-EXEC-PASS-01")
    seq = TestSequence("PassSeq", "1.0")

    def action_step(dut: DUT, ctx: dict) -> dict:
        return {"name": "power", "value": -3.0}

    seq.add_step(
        TestStep(
            name="Power Check",
            action=action_step,
            limits=[MeasurementLimit("power", "dBm", lower_limit=-5.0, upper_limit=-1.0)],
        )
    )

    executor = TestExecutor()
    res = executor.execute_sequence(dut, seq)

    assert res.overall_verdict == Verdict.PASS
    assert res.failure_code == FailureCode.NONE
    assert len(res.all_measurements) == 1
    assert res.all_measurements[0].passed is True


def test_test_executor_failing_limit_sequence() -> None:
    dut = DUT("SN-EXEC-FAIL-01")
    seq = TestSequence("FailSeq", "1.0")

    def action_step(dut: DUT, ctx: dict) -> dict:
        return {"name": "power", "value": -9.0}

    seq.add_step(
        TestStep(
            name="Power Check",
            action=action_step,
            limits=[MeasurementLimit("power", "dBm", lower_limit=-5.0, upper_limit=-1.0)],
        )
    )

    executor = TestExecutor()
    res = executor.execute_sequence(dut, seq)

    assert res.overall_verdict == Verdict.FAIL
    assert res.failure_code == FailureCode.MEASUREMENT_OUT_OF_LIMIT
    assert len(res.all_measurements) == 1
    assert res.all_measurements[0].passed is False
