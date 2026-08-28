#!/usr/bin/env bash
# LabLink Master Local CI Execution Script
# Reproduces the full Jenkins pipeline locally in sequential stages
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="${PROJECT_ROOT}/python"
VENV_BIN="${PYTHON_DIR}/.venv/bin"

echo "========================================================"
echo "      LABLINK AUTOMATED LOCAL CI QUALITY PIPELINE       "
echo "========================================================"
echo "Project Root: ${PROJECT_ROOT}"
echo ""

# Always execute cleanup on script exit or failure
trap '"${SCRIPT_DIR}/cleanup.sh"' EXIT

# Stage 1: Setup Python Environment
echo "=== Stage 1: Setup Python Environment ==="
"${SCRIPT_DIR}/setup_python.sh"
echo ""

# Stage 2: Python Static Quality Checks
echo "=== Stage 2: Python Static Quality Checks ==="
"${SCRIPT_DIR}/run_python_quality.sh"
echo ""

# Stage 3: Python Test Suite
echo "=== Stage 3: Python Test Suite ==="
"${SCRIPT_DIR}/run_python_tests.sh"
echo ""

# Stage 4: Start PostgreSQL Service & Database Migrations
echo "=== Stage 4: Start PostgreSQL Service & Database Migrations ==="
"${SCRIPT_DIR}/start_postgres.sh"
"${SCRIPT_DIR}/wait_for_postgres.sh"
"${SCRIPT_DIR}/migrate_database.sh"
echo ""

# Stage 5: .NET Build, Format & Test Suite
echo "=== Stage 5: .NET Build & Quality Gates ==="
"${SCRIPT_DIR}/run_dotnet_tests.sh"
echo ""

# Stage 6: Docker Compose Config Validation
echo "=== Stage 6: Docker Compose Config Validation ==="
docker compose -f "${PROJECT_ROOT}/docker/docker-compose.yml" config >/dev/null
echo "[+] Docker Compose configuration validated successfully."
echo ""

# Stage 7: Start REST API & Integration Smoke Test
echo "=== Stage 7: Start REST API & Smoke Verification ==="
"${SCRIPT_DIR}/start_api.sh"
"${SCRIPT_DIR}/run_integration_tests.sh"
echo ""

# Stage 8: High-Volume Manufacturing Simulation Demo
echo "=== Stage 8: High-Volume Manufacturing Simulation (100 DUTs) ==="
PYTHON_CMD="${VENV_BIN}/python"
if [ ! -f "${PYTHON_CMD}" ]; then PYTHON_CMD="python3"; fi
PYTHONPATH="${PYTHON_DIR}:${PYTHONPATH:-}" "${PYTHON_CMD}" -m lablink.manufacturing.run_demo --duts 100 --seed 42
echo ""

echo "========================================================"
echo "      LABLINK LOCAL CI PIPELINE COMPLETED CLEANLY!      "
echo "========================================================"
