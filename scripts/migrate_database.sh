#!/usr/bin/env bash
# LabLink EF Core Database Migration Execution Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOTNET_API_DIR="${PROJECT_ROOT}/dotnet/LabLink.Api"

DB_HOST="${LABLINK_DB_HOST:-127.0.0.1}"
DB_PORT="${LABLINK_DB_PORT:-5432}"
DB_NAME="${LABLINK_DB_NAME:-lablink_dev}"
DB_USER="${LABLINK_DB_USER:-sarathpatti}"
DB_PASS="${LABLINK_DB_PASSWORD:-}"

CONNECTION_STRING="Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASS}"

echo "=== Executing EF Core Database Migrations ==="
echo "Target DB: ${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Ensure dotnet-ef tool is available in PATH
export PATH="${HOME}/.dotnet/tools:${PATH}"

cd "${DOTNET_API_DIR}"

if command -v dotnet-ef >/dev/null 2>&1 || dotnet ef --version >/dev/null 2>&1; then
    echo "[+] Applying EF Core database migrations via 'dotnet ef database update'..."
    dotnet ef database update --connection "${CONNECTION_STRING}"
    echo "[+] Database migration applied successfully."
else
    echo "[-] Error: 'dotnet-ef' tool not found. Please install dotnet-ef tool or ensure PATH is configured." >&2
    exit 1
fi
