#!/usr/bin/env bash
# LabLink Build Artifact and Cache Cleanup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Cleaning LabLink Build Artifacts and Caches ==="
echo "Target Root: ${PROJECT_ROOT}"

# Remove Python cache directories safely
find "${PROJECT_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove .NET build artifacts safely
find "${PROJECT_ROOT}/dotnet" -type d -name "bin" -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}/dotnet" -type d -name "obj" -exec rm -rf {} + 2>/dev/null || true

echo "[+] Cleanup complete."
