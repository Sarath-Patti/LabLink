#!/usr/bin/env bash
# LabLink Development Environment Setup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== LabLink Development Environment Setup ==="
echo "Project Root: ${PROJECT_ROOT}"

# Check Python installation
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION="$(python3 --version)"
    echo "[+] Found Python: ${PYTHON_VERSION}"
else
    echo "[-] Error: python3 is required but not installed." >&2
    exit 1
fi

# Check .NET SDK installation (optional notice)
if command -v dotnet >/dev/null 2>&1; then
    DOTNET_VERSION="$(dotnet --version)"
    echo "[+] Found .NET SDK: ${DOTNET_VERSION}"
else
    echo "[!] Notice: dotnet SDK not found in PATH. Install .NET 8.0+ for C# service layer development."
fi

# Setup Virtual Environment if requested
VENV_DIR="${PROJECT_ROOT}/python/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "[+] Creating Python virtual environment at python/.venv..."
    python3 -m venv "${VENV_DIR}"
    echo "[+] Virtual environment created."
else
    echo "[+] Virtual environment already exists at python/.venv."
fi

echo ""
echo "Setup script completed safely."
echo "To activate the Python virtual environment, run:"
echo "  source python/.venv/bin/activate"
