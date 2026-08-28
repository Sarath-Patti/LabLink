#!/usr/bin/env bash
# LabLink Integration & API Smoke Test Execution Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

API_PORT="${LABLINK_API_PORT:-5099}"
API_URL="http://localhost:${API_PORT}"

echo "=== Running Integration & API Smoke Test Suite ==="
echo "Target API: ${API_URL}"

cd "${PYTHON_DIR}"

PYTHON_CMD="${VENV_BIN}/python"
if [ ! -f "${PYTHON_CMD}" ]; then PYTHON_CMD="python3"; fi

# Execute API client smoke test
"${PYTHON_CMD}" -c "
import sys
from lablink.integration.api_client import LabLinkAPIClient

client = LabLinkAPIClient('${API_URL}')

# 1. Health check
h = client.health_check()
print(f'[+] Health status: {h}')
assert h['status'] == 'Healthy'
assert h['service'] == 'LabLink.Api'

# 2. Create test case
tc = client.create_test_case(name='ci_integration_test_case', description='CI smoke test case', suite='ci', category='smoke')
print(f'[+] Created Test Case: {tc[\"id\"]}')

# 3. Create test run
tr = client.create_test_run(name='ci_pipeline_run_01', trigger='JenkinsCI', environment='CI')
run_id = tr['id']
print(f'[+] Created Test Run: {run_id}')

# 4. Ingest passed and failed test results
res1 = client.submit_test_result(run_id, test_name='ci_step_passed', status='Passed', duration=0.10)
res2 = client.submit_test_result(run_id, test_name='ci_step_failed', status='Failed', duration=0.35, error_message='Expected CI validation exception')
print(f'[+] Ingested 2 test results for run {run_id}')

# 5. Complete test run
completed = client.complete_test_run(run_id, status='Completed')
print(f'[+] Completed Test Run: {completed}')
assert completed['status'] == 'Completed'
assert completed['totalTests'] == 2
assert completed['passedTests'] == 1
assert completed['failedTests'] == 1

# 6. Retrieve test run and results
retrieved_run = client.get_test_run(run_id)
assert retrieved_run['totalTests'] == 2

results = client.get_test_results(run_id)
assert len(results) == 2

print('[+] REST API Integration & Smoke Test Passed Cleanly!')
"

echo "[+] API Integration workflow verification succeeded!"
