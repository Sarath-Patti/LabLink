#!/usr/bin/env bash
# LabLink PostgreSQL Readiness Polling Script
set -euo pipefail

DB_HOST="${LABLINK_DB_HOST:-127.0.0.1}"
DB_PORT="${LABLINK_DB_PORT:-5432}"
MAX_RETRIES=30
RETRY_INTERVAL=1

echo "=== Waiting for PostgreSQL readiness at ${DB_HOST}:${DB_PORT} ==="

RETRIES=0
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" >/dev/null 2>&1 || nc -z "${DB_HOST}" "${DB_PORT}" >/dev/null 2>&1 || (exec 3<>/dev/tcp/"${DB_HOST}"/"${DB_PORT}") 2>/dev/null; do
    RETRIES=$((RETRIES + 1))
    if [ "${RETRIES}" -ge "${MAX_RETRIES}" ]; then
        echo "[-] Error: Timed out waiting for PostgreSQL to become ready after ${MAX_RETRIES} seconds." >&2
        exit 1
    fi
    echo "[*] Waiting for PostgreSQL (${RETRIES}/${MAX_RETRIES})..."
    sleep "${RETRY_INTERVAL}"
done

echo "[+] PostgreSQL service is ready and accepting connections."
