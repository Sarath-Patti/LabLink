#!/usr/bin/env bash
# LabLink ASP.NET Core API Background Process Startup & Health Polling Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOTNET_API_DIR="${PROJECT_ROOT}/dotnet/LabLink.Api"
PID_FILE="${SCRIPT_DIR}/.api.pid"
LOG_FILE="${PROJECT_ROOT}/api_ci.log"

API_PORT="${LABLINK_API_PORT:-5099}"
API_URL="http://localhost:${API_PORT}"
HEALTH_URL="${API_URL}/api/v1/health"

echo "=== Starting LabLink.Api Service ==="
echo "Target URL: ${API_URL}"

# If a process is already running via PID file, terminate it
if [ -f "${PID_FILE}" ]; then
    OLD_PID="$(cat "${PID_FILE}")"
    if kill -0 "${OLD_PID}" 2>/dev/null; then
        echo "[+] Terminating previous API process (PID: ${OLD_PID})..."
        kill -15 "${OLD_PID}" 2>/dev/null || kill -9 "${OLD_PID}" 2>/dev/null || true
    fi
    rm -f "${PID_FILE}"
fi

# Launch API background process and redirect output to api_ci.log
cd "${DOTNET_API_DIR}"
dotnet run --project LabLink.Api.csproj --urls "${API_URL}" > "${LOG_FILE}" 2>&1 &
API_PID=$!
echo "${API_PID}" > "${PID_FILE}"
echo "[+] LabLink.Api started in background (PID: ${API_PID}, Log: api_ci.log)"

# Wait for API Health Endpoint
MAX_RETRIES=30
RETRY_INTERVAL=1
RETRIES=0

echo "[+] Polling API health endpoint at ${HEALTH_URL}..."

until curl -s "${HEALTH_URL}" | grep -q '"status":"Healthy"'; do
    RETRIES=$((RETRIES + 1))
    if [ "${RETRIES}" -ge "${MAX_RETRIES}" ]; then
        echo "[-] Error: LabLink.Api failed to become Healthy after ${MAX_RETRIES} seconds." >&2
        echo "=== API STDOUT / STDERR LOG ===" >&2
        cat "${LOG_FILE}" >&2
        exit 1
    fi
    sleep "${RETRY_INTERVAL}"
done

echo "[+] LabLink.Api service is Healthy!"
