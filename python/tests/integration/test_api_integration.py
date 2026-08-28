"""
Python ↔ C# ASP.NET Core API Integration Test.

Launches a local LabLink.Api server instance and executes end-to-end test management,
test run lifecycle, result ingestion, and device/instrument registration over HTTP.
"""

import subprocess
from collections.abc import Generator

import pytest

from lablink.integration.api_client import LabLinkAPIClient
from tests.utilities.helpers import wait_until_condition


@pytest.fixture(scope="module")
def api_server() -> Generator[str, None, None]:
    """
    Launch local LabLink.Api ASP.NET Core Web API instance for integration testing.
    """
    base_url = "http://localhost:5099"
    dotnet_cmd = [
        "dotnet",
        "run",
        "--project",
        "../dotnet/LabLink.Api/LabLink.Api.csproj",
        "--urls",
        base_url,
    ]

    proc = subprocess.Popen(
        dotnet_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    client = LabLinkAPIClient(base_url)

    def is_healthy() -> bool:
        try:
            h = client.health_check()
            return h.get("status") == "Healthy"
        except (RuntimeError, OSError):
            return False

    try:
        try:
            wait_until_condition(is_healthy, timeout=15.0, interval=0.5)
        except TimeoutError:
            proc.kill()
            stdout, stderr = proc.communicate()
            pytest.fail(
                f"LabLink.Api server failed to start on {base_url}.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            )

        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.integration
def test_python_to_csharp_api_integration_workflow(api_server: str) -> None:
    """
    Verify complete Python ↔ C# REST API integration workflow:
    1. Health check status query.
    2. Test Case registration.
    3. Test Run creation.
    4. Test Result ingestion.
    5. Test Run completion & aggregation metric assertion.
    6. Device & Instrument registration.
    """
    client = LabLinkAPIClient(api_server)

    # 1. Health status query
    health = client.health_check()
    assert health["status"] == "Healthy"
    assert health["version"] == "0.9.0"

    # 2. Register Test Case
    tc = client.create_test_case(
        name="test_opm_functional_sweep",
        description="Automated OPM power measurement sweep",
        suite="functional",
        category="optical",
    )
    assert tc["name"] == "test_opm_functional_sweep"
    tc_id = tc["id"]

    # 3. Create Test Run
    run = client.create_test_run(
        name="pytest_automated_run_01",
        trigger="PytestIntegration",
        environment="TestLab",
    )
    assert run["status"] == "Created"
    run_id = run["id"]

    # 4. Submit Test Results
    res1 = client.submit_test_result(
        run_id=run_id,
        test_name="test_opm_wavelength_tuning",
        status="Passed",
        duration=0.12,
        test_case_id=tc_id,
    )
    assert res1["status"] == "Passed"

    res2 = client.submit_test_result(
        run_id=run_id,
        test_name="test_optical_switch_route_failure",
        status="Failed",
        duration=0.45,
        error_message="Matrix route hardware timeout",
    )
    assert res2["status"] == "Failed"

    # Verify results listing
    results = client.get_test_results(run_id)
    assert len(results) == 2

    # 5. Complete Test Run
    completed_run = client.complete_test_run(run_id, status="Completed")
    assert completed_run["status"] == "Completed"
    assert completed_run["totalTests"] == 2
    assert completed_run["passedTests"] == 1
    assert completed_run["failedTests"] == 1
    assert completed_run["skippedTests"] == 0

    # 6. Register Device and Instrument
    device = client.register_device(
        name="lab_core_switch",
        device_type="NetworkSwitch",
        model="Cisco-Nexus-9000",
        address="192.168.1.10:5025",
        protocol="SCPI",
    )
    assert device["name"] == "lab_core_switch"

    instrument = client.register_instrument(
        name="lab_opm_01",
        instrument_type="OpticalPowerMeter",
        model="Keysight-N5767A",
        address="127.0.0.1:5025",
    )
    assert instrument["name"] == "lab_opm_01"
