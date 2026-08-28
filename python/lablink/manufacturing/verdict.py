"""
Verdict Engine & Machine-Readable Failure Classification.

Provides deterministic rules for step and overall DUT verdict calculation and stable failure codes.
"""

from enum import Enum


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class FailureCode(str, Enum):
    NONE = "NONE"
    INSTRUMENT_CONNECTION = "INSTRUMENT_CONNECTION"
    INSTRUMENT_TIMEOUT = "INSTRUMENT_TIMEOUT"
    MEASUREMENT_OUT_OF_LIMIT = "MEASUREMENT_OUT_OF_LIMIT"
    NETWORK_CONNECTIVITY = "NETWORK_CONNECTIVITY"
    VLAN_CONFIGURATION = "VLAN_CONFIGURATION"
    PACKET_LOSS = "PACKET_LOSS"
    TRAFFIC_FAILURE = "TRAFFIC_FAILURE"
    TEST_TIMEOUT = "TEST_TIMEOUT"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    SOFTWARE_ERROR = "SOFTWARE_ERROR"


class VerdictEngine:
    @staticmethod
    def calculate_overall_verdict(step_verdicts: list[Verdict]) -> Verdict:
        if not step_verdicts:
            return Verdict.SKIPPED

        if any(v == Verdict.ERROR for v in step_verdicts):
            return Verdict.ERROR
        if any(v == Verdict.FAIL for v in step_verdicts):
            return Verdict.FAIL
        if all(v == Verdict.SKIPPED for v in step_verdicts):
            return Verdict.SKIPPED
        return Verdict.PASS
