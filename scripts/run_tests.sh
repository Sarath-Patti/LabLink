#!/usr/bin/env bash
# LabLink Test Execution Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"

echo "=== LabLink Test Runner ==="

if [ ! -d "${PYTHON_DIR}" ]; then
    echo "[-] Error: Python directory not found at ${PYTHON_DIR}" >&2
    exit 1
fi

cd "${PYTHON_DIR}"

if command -v pytest >/dev/null 2>&1; then
    echo "[+] Running pytest test suite..."
    pytest "$@"
elif [ -f "${PYTHON_DIR}/.venv/bin/pytest" ]; then
    echo "[+] Running pytest from virtual environment..."
    "${PYTHON_DIR}/.venv/bin/pytest" "$@"
else
    echo "[-] Error: pytest is not available. Please install dependencies or activate virtual environment." >&2
    exit 1
fi
