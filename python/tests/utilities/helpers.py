"""
LabLink Test Helper Utilities.

Provides timing measurement, polling predicate synchronization, and execution helpers.
"""

import time
from collections.abc import Callable
from typing import Any


def wait_until_condition(
    predicate: Callable[[], bool],
    timeout: float = 2.0,
    interval: float = 0.05,
    description: str = "condition",
) -> bool:
    """
    Poll a predicate function until it returns True or timeout expires.

    Args:
        predicate: Callable returning boolean condition.
        timeout: Maximum wait timeout in seconds.
        interval: Polling interval in seconds.
        description: Description of target condition for error diagnostics.

    Returns:
        True if condition met within timeout.

    Raises:
        TimeoutError: If condition is not met before timeout expires.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)

    raise TimeoutError(f"Timed out after {timeout}s waiting for {description}.")


def measure_execution_time(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> tuple[Any, float]:
    """
    Execute callable function and measure execution duration in seconds.

    Args:
        func: Target function to execute.
        *args: Positional arguments for function.
        **kwargs: Keyword arguments for function.

    Returns:
        Tuple of (function_result, duration_seconds: float).
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start_time
    return result, duration
