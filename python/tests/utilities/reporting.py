"""
LabLink Structured Test Measurement Result & JSON Exporter.

Provides structured test result representations and JSON export tools
for test automation telemetry.
"""

import datetime
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from lablink.logging import get_logger

logger = get_logger("tests.reporting")


@dataclass
class TestMeasurementResult:
    """Structured representation of an automated test measurement record."""

    __test__ = False  # Instruct pytest not to collect this dataclass as a test suite class

    test_name: str
    category: str
    status: str
    duration_ms: float
    instrument: str
    measurement_name: str
    expected: Any
    actual: Any
    unit: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class JSONResultExporter:
    """
    Export test measurement results to a local JSON report file.
    """

    def __init__(self, output_file: str | Path = "test_results.json") -> None:
        self.output_path = Path(output_file)
        self.records: list[TestMeasurementResult] = []

    def record_result(self, result: TestMeasurementResult) -> None:
        """Add a test measurement record to internal collection."""
        self.records.append(result)
        logger.debug(f"Recorded test result: {result.test_name} [{result.status}]")

    def export(self) -> Path:
        """
        Serialize all recorded test measurement records to output JSON file.

        Returns:
            Path object of written JSON report file.
        """
        data = [asdict(record) for record in self.records]

        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(self.records)} test results to {self.output_path}")
        return self.output_path
