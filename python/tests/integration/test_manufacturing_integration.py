"""
Integration test for Python Manufacturing Engine ↔ C# REST API.
"""

import uuid

import pytest

from lablink.integration.api_client import LabLinkAPIClient
from lablink.manufacturing.dut import DUT
from lablink.manufacturing.simulation import ManufacturingSimulationEngine


@pytest.mark.integration
@pytest.mark.manufacturing
def test_manufacturing_python_to_csharp_api_integration(api_server: str) -> None:
    client = LabLinkAPIClient(api_server)
    health = client.health_check()
    assert health["status"] == "Healthy"

    # 1. Register DUT over API with dynamic serial
    serial = f"SN-INT-MFG-{uuid.uuid4().hex[:8]}"
    dut_dto = client.create_dut(serial, part_number="PN-OPT-100G", hardware_revision="RevC")
    assert dut_dto["serialNumber"] == serial

    # 2. Execute simulation run locally
    engine = ManufacturingSimulationEngine(seed=99)
    seq = engine.build_optical_module_sequence()
    dut = DUT(serial_number=serial)
    exec_res = engine.executor.execute_sequence(dut, seq)

    # 3. Create Manufacturing Run in API
    mfg_run = client.create_manufacturing_run(
        serial,
        station_id=exec_res.station_id,
        sequence_name=exec_res.sequence_name,
        sequence_version=exec_res.sequence_version,
    )
    run_id = mfg_run["id"]

    # 4. Ingest measurements into API
    for m in exec_res.all_measurements:
        meas_dto = client.add_measurement(
            run_id=run_id,
            step_name=m.step_name,
            measurement_name=m.measurement_name,
            value=m.value,
            unit=m.unit,
            lower_limit=m.lower_limit,
            upper_limit=m.upper_limit,
            verdict=m.verdict.value,
            failure_code=m.failure_code.value,
            instrument_source=m.instrument_source,
        )
        assert meas_dto["measurementName"] == m.measurement_name

    # 5. Complete run in API
    completed = client.complete_manufacturing_run(
        run_id=run_id,
        verdict=exec_res.overall_verdict.value,
        failure_code=exec_res.failure_code.value,
        failure_summary=exec_res.failure_summary,
    )
    assert completed["id"] == run_id

    # 6. Retrieve yield analytics
    analytics = client.get_yield_analytics()
    assert analytics["totalUnitsTested"] >= 1
