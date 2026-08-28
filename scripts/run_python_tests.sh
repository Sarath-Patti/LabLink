#!/usr/bin/env bash
# LabLink Python Test Suite Execution Script with JUnit XML Report Output
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

echo "=== Running Python Pytest Suite ==="

cd "${PYTHON_DIR}"

PYTEST_CMD="${VENV_BIN}/pytest"
if [ ! -f "${PYTEST_CMD}" ]; then PYTEST_CMD="pytest"; fi

echo "[+] Executing pytest with JUnit XML report generation..."
"${PYTEST_CMD}" -v --junitxml="${PROJECT_ROOT}/python_test_results.xml" "$@"

echo "[+] Python test suite completed successfully. Report: python_test_results.xml"
