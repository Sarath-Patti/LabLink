"""
Device Under Test (DUT) Abstraction.

Provides unique identification, metadata traceability, and status management for units tested on the manufacturing line.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DUTStatus(str, Enum):
    UNTESTED = "Untested"
    PASSED = "Passed"
    FAILED = "Failed"
    SCRAPPED = "Scrapped"


@dataclass
class DUT:
    serial_number: str
    part_number: str = "PN-OPT-100G"
    hardware_revision: str = "RevA"
    firmware_version: str = "v1.0.0"
    status: DUTStatus = DUTStatus.UNTESTED
    created_at: datetime = field(default_factory=datetime.utcnow)
    dut_id: str | None = None

    def __post_init__(self) -> None:
        if not self.serial_number or not self.serial_number.strip():
            raise ValueError("DUT serial_number must be a non-empty string.")
        self.serial_number = self.serial_number.strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "dut_id": self.dut_id,
            "serial_number": self.serial_number,
            "part_number": self.part_number,
            "hardware_revision": self.hardware_revision,
            "firmware_version": self.firmware_version,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }
