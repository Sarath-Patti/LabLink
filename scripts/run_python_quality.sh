#!/usr/bin/env bash
# LabLink Python Quality Checks Execution Script (Ruff, Black, Mypy)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

echo "=== Running Python Static Quality Checks ==="

cd "${PYTHON_DIR}"

# Determine Python linter executables
RUFF_CMD="${VENV_BIN}/ruff"
BLACK_CMD="${VENV_BIN}/black"
MYPY_CMD="${VENV_BIN}/mypy"

if [ ! -f "${RUFF_CMD}" ]; then RUFF_CMD="ruff"; fi
if [ ! -f "${BLACK_CMD}" ]; then BLACK_CMD="black"; fi
if [ ! -f "${MYPY_CMD}" ]; then MYPY_CMD="mypy"; fi

echo "[1/3] Running Ruff Linter..."
"${RUFF_CMD}" check .

echo "[2/3] Running Black Code Formatter Check..."
"${BLACK_CMD}" --check .

echo "[3/3] Running Mypy Static Type Checker..."
"${MYPY_CMD}" lablink

echo "[+] Python quality checks passed cleanly!"
