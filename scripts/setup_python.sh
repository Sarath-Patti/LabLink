#!/usr/bin/env bash
# LabLink Python Virtual Environment & Dependency Setup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_DIR="${PYTHON_DIR}/.venv"

echo "=== Setting Up LabLink Python Environment ==="
echo "Project Root: ${PROJECT_ROOT}"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[-] Error: python3 is required but not installed." >&2
    exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
    echo "[+] Creating Python virtual environment at python/.venv..."
    python3 -m venv "${VENV_DIR}"
    echo "[+] Virtual environment created."
fi

# Upgrade pip and install package dependencies in editable mode
echo "[+] Upgrading pip and installing lablink dependencies..."
"${VENV_DIR}/bin/pip" install --upgrade pip >/dev/null 2>&1 || true
"${VENV_DIR}/bin/pip" install -e "${PYTHON_DIR}[dev]" >/dev/null

echo "[+] Python environment ready: $("${VENV_DIR}/bin/python" --version)"
