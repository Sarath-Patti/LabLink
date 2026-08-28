"""
Versioned Test Sequence & Step Abstraction.

Structures ordered manufacturing test steps with limits, retry policies, and timeouts.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from lablink.manufacturing.limits import MeasurementLimit


@dataclass
class TestStep:
    name: str
    action: Callable[..., Any]
    identifier: str | None = None
    timeout_sec: float = 5.0
    max_retries: int = 0
    limits: list[MeasurementLimit] = field(default_factory=list)
    enabled: bool = True
    critical: bool = True

    __test__ = False  # Prevent pytest from treating domain class as a test suite

    def __post_init__(self) -> None:
        if not self.identifier:
            self.identifier = self.name.lower().replace(" ", "_")


@dataclass
class TestSequence:
    name: str
    version: str
    steps: list[TestStep] = field(default_factory=list)

    __test__ = False  # Prevent pytest from treating domain class as a test suite

    def add_step(self, step: TestStep) -> None:
        self.steps.append(step)

    def get_enabled_steps(self) -> list[TestStep]:
        return [s for s in self.steps if s.enabled]
