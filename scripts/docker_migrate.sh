#!/usr/bin/env bash
# LabLink Containerized EF Core Database Migration Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOTNET_API_DIR="${PROJECT_ROOT}/dotnet/LabLink.Api"

DB_HOST="${LABLINK_DB_HOST:-127.0.0.1}"
DB_PORT="${LABLINK_DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-lablink_dev}"
DB_USER="${POSTGRES_USER:-sarathpatti}"
DB_PASS="${POSTGRES_PASSWORD:-}"

CONNECTION_STRING="Host=${DB_HOST};Port=${DB_PORT};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASS}"

echo "=== Executing EF Core Migrations against Containerized PostgreSQL ==="
echo "Target DB: ${DB_HOST}:${DB_PORT}/${DB_NAME}"

export PATH="${HOME}/.dotnet/tools:${PATH}"

cd "${DOTNET_API_DIR}"
dotnet ef database update --connection "${CONNECTION_STRING}"

echo "[+] EF Core database migrations applied cleanly."
