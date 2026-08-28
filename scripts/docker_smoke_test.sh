#!/usr/bin/env bash
# LabLink Containerized REST API & Persistence Smoke Test Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

API_PORT="${LABLINK_API_PORT:-5099}"
API_URL="http://localhost:${API_PORT}"

echo "=== Executing Containerized REST API & Persistence Smoke Test ==="
echo "Target API: ${API_URL}"

cd "${PYTHON_DIR}"

PYTHON_CMD="${VENV_BIN}/python"
if [ ! -f "${PYTHON_CMD}" ]; then PYTHON_CMD="python3"; fi

"${PYTHON_CMD}" -c "
import sys
from lablink.integration.api_client import LabLinkAPIClient

client = LabLinkAPIClient('${API_URL}')

# 1. Health check
h = client.health_check()
print(f'[+] Containerized Health Status: {h}')
assert h['status'] == 'Healthy'
assert h['version'] == '0.9.0'
assert h['database'] == 'Connected'

# 2. Create test case
tc = client.create_test_case(name='docker_smoke_test_case', description='Docker containerized smoke test', suite='docker', category='smoke')
print(f'[+] Created Test Case: {tc[\"id\"]}')

# 3. Create test run
tr = client.create_test_run(name='docker_pipeline_run_01', trigger='DockerSmoke', environment='DockerCompose')
run_id = tr['id']
print(f'[+] Created Test Run: {run_id}')

# 4. Ingest passed test result
res = client.submit_test_result(run_id, test_name='docker_step_passed', status='Passed', duration=0.18, test_case_id=tc['id'])
print(f'[+] Ingested result {res[\"id\"]} for run {run_id}')

# 5. Complete test run
completed = client.complete_test_run(run_id, status='Completed')
print(f'[+] Completed Test Run: {completed}')
assert completed['status'] == 'Completed'
assert completed['totalTests'] == 1
assert completed['passedTests'] == 1

# 6. Retrieve test run and results
retrieved_run = client.get_test_run(run_id)
assert retrieved_run['totalTests'] == 1

results = client.get_test_results(run_id)
assert len(results) == 1
assert results[0]['testName'] == 'docker_step_passed'

print('[+] Containerized API Smoke & Persistence Test PASSED CLEANLY!')
"

echo "[+] Docker stack integration verification succeeded!"
