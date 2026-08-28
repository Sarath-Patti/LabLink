"""
Unit tests for VerdictEngine and FailureCode classification.
"""

from lablink.manufacturing.verdict import FailureCode, Verdict, VerdictEngine


def test_verdict_engine_all_pass() -> None:
    verdicts = [Verdict.PASS, Verdict.PASS, Verdict.PASS]
    assert VerdictEngine.calculate_overall_verdict(verdicts) == Verdict.PASS


def test_verdict_engine_single_fail() -> None:
    verdicts = [Verdict.PASS, Verdict.FAIL, Verdict.PASS]
    assert VerdictEngine.calculate_overall_verdict(verdicts) == Verdict.FAIL


def test_verdict_engine_single_error() -> None:
    verdicts = [Verdict.PASS, Verdict.ERROR, Verdict.FAIL]
    assert VerdictEngine.calculate_overall_verdict(verdicts) == Verdict.ERROR


def test_failure_code_values() -> None:
    assert FailureCode.NONE.value == "NONE"
    assert FailureCode.INSTRUMENT_CONNECTION.value == "INSTRUMENT_CONNECTION"
    assert FailureCode.MEASUREMENT_OUT_OF_LIMIT.value == "MEASUREMENT_OUT_OF_LIMIT"
