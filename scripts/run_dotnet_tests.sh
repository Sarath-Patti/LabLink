#!/usr/bin/env bash
# LabLink .NET Build, Format Verification, and xUnit Test Execution Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOTNET_DIR="${PROJECT_ROOT}/dotnet"
API_PROJECT="${DOTNET_DIR}/LabLink.Api/LabLink.Api.csproj"
TEST_PROJECT="${DOTNET_DIR}/LabLink.Api.Tests/LabLink.Api.Tests.csproj"

echo "=== Running .NET Build and Quality Verification ==="

if ! command -v dotnet >/dev/null 2>&1; then
    echo "[-] Error: dotnet SDK is required but not installed." >&2
    exit 1
fi

echo "[1/3] Building .NET Solution..."
dotnet restore "${API_PROJECT}"
dotnet build "${API_PROJECT}" --no-restore

echo "[2/3] Verifying .NET Code Formatting..."
dotnet format "${API_PROJECT}" --verify-no-changes

echo "[3/3] Running xUnit Test Suite..."
dotnet test "${TEST_PROJECT}" --logger "trx;LogFileName=dotnet_test_results.trx"

echo "[+] .NET quality and test suite passed cleanly!"
