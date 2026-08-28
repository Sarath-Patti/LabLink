"""
Unit tests for limit evaluation engine.
"""

from lablink.manufacturing.limits import ComparisonType, LimitEvaluator, MeasurementLimit


def test_range_limit_evaluation_pass() -> None:
    limit = MeasurementLimit("optical_power", "dBm", lower_limit=-5.0, upper_limit=-1.0)
    res = LimitEvaluator.evaluate(limit, -3.2)
    assert res.passed is True
    assert res.error_message is None


def test_range_limit_evaluation_fail_low() -> None:
    limit = MeasurementLimit("optical_power", "dBm", lower_limit=-5.0, upper_limit=-1.0)
    res = LimitEvaluator.evaluate(limit, -6.5)
    assert res.passed is False
    assert "below lower limit" in res.error_message


def test_equal_limit_evaluation_pass() -> None:
    limit = MeasurementLimit(
        "vlan_id", "vlan", expected_value=100, comparison_type=ComparisonType.EQUAL
    )
    res = LimitEvaluator.evaluate(limit, 100)
    assert res.passed is True


def test_equal_limit_evaluation_fail() -> None:
    limit = MeasurementLimit(
        "vlan_id", "vlan", expected_value=100, comparison_type=ComparisonType.EQUAL
    )
    res = LimitEvaluator.evaluate(limit, 200)
    assert res.passed is False
    assert "does not match expected" in res.error_message
