"""
Configurable Limits & Limit Evaluator.

Evaluates numeric or string measurements against lower, upper, or exact expected values.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ComparisonType(str, Enum):
    RANGE = "RANGE"
    LESS_THAN_EQUAL = "LESS_THAN_EQUAL"
    GREATER_THAN_EQUAL = "GREATER_THAN_EQUAL"
    EQUAL = "EQUAL"


@dataclass
class MeasurementLimit:
    measurement_name: str
    unit: str
    lower_limit: float | None = None
    upper_limit: float | None = None
    expected_value: Any | None = None
    comparison_type: ComparisonType = ComparisonType.RANGE


@dataclass
class LimitEvaluationResult:
    measurement_name: str
    value: Any
    unit: str
    passed: bool
    lower_limit: float | None
    upper_limit: float | None
    expected_value: Any | None
    error_message: str | None = None


class LimitEvaluator:
    @staticmethod
    def evaluate(limit: MeasurementLimit, value: Any) -> LimitEvaluationResult:
        if value is None:
            return LimitEvaluationResult(
                measurement_name=limit.measurement_name,
                value=None,
                unit=limit.unit,
                passed=False,
                lower_limit=limit.lower_limit,
                upper_limit=limit.upper_limit,
                expected_value=limit.expected_value,
                error_message="Measured value is None.",
            )

        passed = True
        err: str | None = None

        if limit.comparison_type == ComparisonType.RANGE:
            num_val = float(value)
            if limit.lower_limit is not None and num_val < limit.lower_limit:
                passed = False
                err = f"Value {num_val} {limit.unit} below lower limit {limit.lower_limit} {limit.unit}"
            elif limit.upper_limit is not None and num_val > limit.upper_limit:
                passed = False
                err = f"Value {num_val} {limit.unit} exceeds upper limit {limit.upper_limit} {limit.unit}"

        elif limit.comparison_type == ComparisonType.LESS_THAN_EQUAL:
            num_val = float(value)
            if limit.upper_limit is not None and num_val > limit.upper_limit:
                passed = False
                err = f"Value {num_val} {limit.unit} exceeds upper bound {limit.upper_limit} {limit.unit}"

        elif limit.comparison_type == ComparisonType.GREATER_THAN_EQUAL:
            num_val = float(value)
            if limit.lower_limit is not None and num_val < limit.lower_limit:
                passed = False
                err = f"Value {num_val} {limit.unit} below lower bound {limit.lower_limit} {limit.unit}"

        elif limit.comparison_type == ComparisonType.EQUAL:
            if str(value).strip().lower() != str(limit.expected_value).strip().lower():
                passed = False
                err = f"Value '{value}' does not match expected '{limit.expected_value}'"

        return LimitEvaluationResult(
            measurement_name=limit.measurement_name,
            value=value,
            unit=limit.unit,
            passed=passed,
            lower_limit=limit.lower_limit,
            upper_limit=limit.upper_limit,
            expected_value=limit.expected_value,
            error_message=err,
        )
