"""
LabLink HTTP API Client for Python ↔ C# REST API Integration.

Provides standard-library HTTP operations for interacting with the LabLink.Api ASP.NET Core service layer,
including test case management, test run lifecycles, test result ingestion, device/instrument registrations,
and v1.0 manufacturing execution, measurement traceability, and yield analytics endpoints.
"""

import json
import urllib.error
import urllib.request
from typing import Any

from lablink.logging import get_logger

logger = get_logger("integration.api_client")


class LabLinkAPIClient:
    """
    Standard-library HTTP client for the LabLink C#/.NET REST API service layer.
    """

    def __init__(self, base_url: str = "http://localhost:5000") -> None:
        self.base_url: str = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = json.dumps(payload).encode("utf-8") if payload is not None else None

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                resp_bytes = resp.read()
                if not resp_bytes:
                    return None
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"HTTPError [{e.code}] {url}: {error_body}")
            try:
                parsed_err = json.loads(error_body)
                raise RuntimeError(
                    f"API Error [{e.code}]: {parsed_err.get('message', error_body)}"
                ) from e
            except json.JSONDecodeError:
                raise RuntimeError(f"HTTP Error [{e.code}]: {error_body}") from e
        except urllib.error.URLError as e:
            logger.error(f"URLError {url}: {e.reason}")
            raise RuntimeError(f"Failed to connect to LabLink.Api at {url}: {e.reason}") from e

    def health_check(self) -> dict[str, Any]:
        """Query GET /api/v1/health status endpoint."""
        res = self._request("GET", "/api/v1/health")
        return res if isinstance(res, dict) else {}

    def create_test_case(
        self,
        name: str,
        description: str = "",
        suite: str = "functional",
        category: str = "optical",
        enabled: bool = True,
    ) -> dict[str, Any]:
        """POST /api/v1/test-cases"""
        payload = {
            "name": name,
            "description": description,
            "suite": suite,
            "category": category,
            "enabled": enabled,
        }
        res = self._request("POST", "/api/v1/test-cases", payload)
        return res if isinstance(res, dict) else {}

    def get_test_cases(self) -> list[dict[str, Any]]:
        """GET /api/v1/test-cases"""
        res = self._request("GET", "/api/v1/test-cases")
        return res if isinstance(res, list) else []

    def create_test_run(
        self,
        name: str,
        trigger: str = "Manual",
        environment: str = "Development",
    ) -> dict[str, Any]:
        """POST /api/v1/test-runs"""
        payload = {"name": name, "trigger": trigger, "environment": environment}
        res = self._request("POST", "/api/v1/test-runs", payload)
        return res if isinstance(res, dict) else {}

    def get_test_run(self, run_id: str) -> dict[str, Any]:
        """GET /api/v1/test-runs/{run_id}"""
        res = self._request("GET", f"/api/v1/test-runs/{run_id}")
        return res if isinstance(res, dict) else {}

    def submit_test_result(
        self,
        run_id: str,
        test_name: str,
        status: str,
        duration: float = 0.0,
        error_message: str | None = None,
        test_case_id: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v1/test-runs/{run_id}/results"""
        payload = {
            "testName": test_name,
            "testCaseId": test_case_id,
            "status": status,
            "duration": max(0.0, duration),
            "errorMessage": error_message,
        }
        res = self._request("POST", f"/api/v1/test-runs/{run_id}/results", payload)
        return res if isinstance(res, dict) else {}

    def get_test_results(self, run_id: str) -> list[dict[str, Any]]:
        """GET /api/v1/test-runs/{run_id}/results"""
        res = self._request("GET", f"/api/v1/test-runs/{run_id}/results")
        return res if isinstance(res, list) else []

    def complete_test_run(self, run_id: str, status: str = "Completed") -> dict[str, Any]:
        """POST /api/v1/test-runs/{run_id}/complete"""
        payload = {"status": status}
        res = self._request("POST", f"/api/v1/test-runs/{run_id}/complete", payload)
        return res if isinstance(res, dict) else {}

    def register_device(
        self,
        name: str,
        device_type: str = "GenericDevice",
        model: str = "",
        address: str = "",
        protocol: str = "TCP",
        enabled: bool = True,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """POST /api/v1/devices"""
        payload = {
            "name": name,
            "type": device_type,
            "model": model,
            "address": address,
            "protocol": protocol,
            "enabled": enabled,
            "metadata": metadata or {},
        }
        res = self._request("POST", "/api/v1/devices", payload)
        return res if isinstance(res, dict) else {}

    def register_instrument(
        self,
        name: str,
        instrument_type: str,
        model: str = "",
        interface_type: str = "TCPIP",
        address: str = "",
        enabled: bool = True,
    ) -> dict[str, Any]:
        """POST /api/v1/instruments"""
        payload = {
            "name": name,
            "type": instrument_type,
            "model": model,
            "interface": interface_type,
            "address": address,
            "enabled": enabled,
        }
        res = self._request("POST", "/api/v1/instruments", payload)
        return res if isinstance(res, dict) else {}

    # --- v1.0 Manufacturing Endpoints ---

    def create_dut(
        self,
        serial_number: str,
        part_number: str = "PN-OPT-100G",
        hardware_revision: str = "RevA",
        firmware_version: str = "v1.0.0",
    ) -> dict[str, Any]:
        """POST /api/v1/duts"""
        payload = {
            "serialNumber": serial_number,
            "partNumber": part_number,
            "hardwareRevision": hardware_revision,
            "firmwareVersion": firmware_version,
        }
        res = self._request("POST", "/api/v1/duts", payload)
        return res if isinstance(res, dict) else {}

    def get_dut_by_id(self, dut_id: str) -> dict[str, Any]:
        """GET /api/v1/duts/{dut_id}"""
        res = self._request("GET", f"/api/v1/duts/{dut_id}")
        return res if isinstance(res, dict) else {}

    def get_dut_by_serial(self, serial_number: str) -> dict[str, Any]:
        """GET /api/v1/duts/serial/{serial_number}"""
        res = self._request("GET", f"/api/v1/duts/serial/{serial_number}")
        return res if isinstance(res, dict) else {}

    def create_manufacturing_run(
        self,
        serial_number: str,
        station_id: str = "Station-01",
        sequence_name: str = "OpticalSequence",
        sequence_version: str = "1.0",
        software_version: str = "1.0.0",
    ) -> dict[str, Any]:
        """POST /api/v1/manufacturing/runs"""
        payload = {
            "serialNumber": serial_number,
            "stationId": station_id,
            "sequenceName": sequence_name,
            "sequenceVersion": sequence_version,
            "softwareVersion": software_version,
        }
        res = self._request("POST", "/api/v1/manufacturing/runs", payload)
        return res if isinstance(res, dict) else {}

    def add_measurement(
        self,
        run_id: str,
        step_name: str,
        measurement_name: str,
        value: Any,
        unit: str = "",
        lower_limit: float | None = None,
        upper_limit: float | None = None,
        expected_value: str | None = None,
        verdict: str = "Passed",
        failure_code: str = "NONE",
        instrument_source: str = "Simulator",
    ) -> dict[str, Any]:
        """POST /api/v1/manufacturing/runs/{run_id}/measurements"""
        try:
            num_val = float(value)
        except (ValueError, TypeError):
            num_val = 1.0 if str(value).upper() in ("CONNECTED", "PASS", "TRUE") else 0.0
            if expected_value is None:
                expected_value = str(value)

        payload = {
            "stepName": step_name,
            "measurementName": measurement_name,
            "value": num_val,
            "unit": unit,
            "lowerLimit": lower_limit,
            "upperLimit": upper_limit,
            "expectedValue": expected_value,
            "verdict": verdict,
            "failureCode": failure_code,
            "instrumentSource": instrument_source,
        }
        res = self._request("POST", f"/api/v1/manufacturing/runs/{run_id}/measurements", payload)
        return res if isinstance(res, dict) else {}

    def complete_manufacturing_run(
        self,
        run_id: str,
        verdict: str = "Completed",
        failure_code: str = "NONE",
        failure_summary: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v1/manufacturing/runs/{run_id}/complete"""
        payload = {
            "verdict": verdict,
            "failureCode": failure_code,
            "failureSummary": failure_summary,
        }
        res = self._request("POST", f"/api/v1/manufacturing/runs/{run_id}/complete", payload)
        return res if isinstance(res, dict) else {}

    def get_run_measurements(self, run_id: str) -> list[dict[str, Any]]:
        """GET /api/v1/manufacturing/runs/{run_id}/measurements"""
        res = self._request("GET", f"/api/v1/manufacturing/runs/{run_id}/measurements")
        return res if isinstance(res, list) else []

    def get_yield_analytics(self) -> dict[str, Any]:
        """GET /api/v1/manufacturing/analytics/yield"""
        res = self._request("GET", "/api/v1/manufacturing/analytics/yield")
        return res if isinstance(res, dict) else {}
