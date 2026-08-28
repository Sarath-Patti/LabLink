#!/usr/bin/env bash
# LabLink Containerized REST API & Persistence Smoke Test Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

API_PORT="${LABLINK_API_PORT:-5099}"
API_URL="http://localhost:${API_PORT}"

echo "=== Executing Containerized REST API & Manufacturing Persistence Smoke Test ==="
echo "Target API: ${API_URL}"

cd "${PYTHON_DIR}"

PYTHON_CMD="${VENV_BIN}/python"
if [ ! -f "${PYTHON_CMD}" ]; then PYTHON_CMD="python3"; fi

"${PYTHON_CMD}" -c "
import sys
from lablink.integration.api_client import LabLinkAPIClient
from lablink.manufacturing.simulation import ManufacturingSimulationEngine
from lablink.manufacturing.dut import DUT

client = LabLinkAPIClient('${API_URL}')

# 1. Health check
h = client.health_check()
print(f'[+] Containerized Health Status: {h}')
assert h['status'] == 'Healthy'
assert h['version'] == '1.0.0'
assert h['database'] == 'Connected'

# 2. Register DUT
serial = 'SN-DOCKER-MFG-001'
dut_dto = client.create_dut(serial, part_number='PN-OPT-100G', hardware_revision='RevB')
print(f'[+] Registered DUT: {dut_dto[\"serialNumber\"]}')

# 3. Execute Manufacturing Simulation
engine = ManufacturingSimulationEngine(seed=42)
seq = engine.build_optical_module_sequence()
dut = DUT(serial_number=serial)
exec_res = engine.executor.execute_sequence(dut, seq)

# 4. Create Manufacturing Run
run_dto = client.create_manufacturing_run(serial, station_id=exec_res.station_id, sequence_name=exec_res.sequence_name, sequence_version=exec_res.sequence_version)
run_id = run_dto['id']
print(f'[+] Created Manufacturing Run: {run_id}')

# 5. Add Measurement Records
for m in exec_res.all_measurements:
    client.add_measurement(
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

# 6. Complete Manufacturing Run
completed = client.complete_manufacturing_run(run_id, verdict=exec_res.overall_verdict.value, failure_code=exec_res.failure_code.value)
print(f'[+] Completed Manufacturing Run: {completed}')
assert completed['verdict'] == 'Completed'

# 7. Query Yield Analytics
yield_dto = client.get_yield_analytics()
print(f'[+] Yield Analytics: {yield_dto}')
assert yield_dto['totalUnitsTested'] >= 1

print('[+] Containerized API & Manufacturing Persistence Smoke Test PASSED CLEANLY!')
"

echo "[+] Docker stack integration verification succeeded!"
