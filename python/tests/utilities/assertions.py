"""
LabLink Custom Measurement Assertion Helpers for Test Automation.

Provides domain-specific numerical assertions with informative error reporting context.
"""


def assert_within_tolerance(
    actual: float, expected: float, tolerance: float, message: str = ""
) -> None:
    """
    Assert that actual numerical value is within expected ± tolerance.

    Args:
        actual: Measured numeric value.
        expected: Target expected value.
        tolerance: Absolute allowable difference tolerance.
        message: Optional diagnostic context message.
    """
    diff = abs(actual - expected)
    prefix = f"{message}: " if message else ""
    assert (
        diff <= tolerance
    ), f"{prefix}Expected {expected} ± {tolerance}, but got {actual} (diff={diff:.6f})"


def assert_greater_than(actual: float, threshold: float, message: str = "") -> None:
    """
    Assert that actual numerical value is strictly greater than threshold.

    Args:
        actual: Measured numeric value.
        threshold: Minimum threshold value.
        message: Optional diagnostic context message.
    """
    prefix = f"{message}: " if message else ""
    assert actual > threshold, f"{prefix}Expected value > {threshold}, but got {actual}"


def assert_less_than(actual: float, threshold: float, message: str = "") -> None:
    """
    Assert that actual numerical value is strictly less than threshold.

    Args:
        actual: Measured numeric value.
        threshold: Maximum threshold value.
        message: Optional diagnostic context message.
    """
    prefix = f"{message}: " if message else ""
    assert actual < threshold, f"{prefix}Expected value < {threshold}, but got {actual}"


def assert_in_range(value: float, minimum: float, maximum: float, message: str = "") -> None:
    """
    Assert that numerical value falls inclusively within [minimum, maximum] range.

    Args:
        value: Numeric value to evaluate.
        minimum: Inclusive lower bound.
        maximum: Inclusive upper bound.
        message: Optional diagnostic context message.
    """
    prefix = f"{message}: " if message else ""
    assert (
        minimum <= value <= maximum
    ), f"{prefix}Expected value in range [{minimum}, {maximum}], but got {value}"
