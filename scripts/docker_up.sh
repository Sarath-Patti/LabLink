#!/usr/bin/env bash
# LabLink Docker Compose Stack Build & Startup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose.yml"
API_PROJECT="${PROJECT_ROOT}/dotnet/LabLink.Api/LabLink.Api.csproj"
PUBLISH_DIR="${PROJECT_ROOT}/dotnet/LabLink.Api/bin/Release/net8.0/publish"

API_PORT="${LABLINK_API_PORT:-5099}"
API_URL="http://localhost:${API_PORT}"
HEALTH_URL="${API_URL}/api/v1/health"

echo "=== Building and Starting LabLink Docker Compose Stack ==="
echo "Compose File: ${DOCKER_COMPOSE_FILE}"

if ! command -v docker >/dev/null 2>&1; then
    echo "[-] Error: docker binary is required but not found on PATH." >&2
    exit 1
fi

echo "[1/4] Publishing .NET Release binaries..."
dotnet publish "${API_PROJECT}" -c Release -o "${PUBLISH_DIR}" >/dev/null

echo "[2/4] Building Docker images..."
docker compose -f "${DOCKER_COMPOSE_FILE}" build

echo "[3/4] Starting containerized services (postgres, lablink-api)..."
docker compose -f "${DOCKER_COMPOSE_FILE}" up -d

echo "[4/4] Waiting for container health checks..."
MAX_RETRIES=30
RETRY_INTERVAL=1
RETRIES=0

until curl -s "${HEALTH_URL}" | grep -q '"status":"Healthy"'; do
    RETRIES=$((RETRIES + 1))
    if [ "${RETRIES}" -ge "${MAX_RETRIES}" ]; then
        echo "[-] Error: Containerized LabLink.Api failed to become Healthy after ${MAX_RETRIES} seconds." >&2
        echo "=== DOCKER COMPOSE LOGS ===" >&2
        docker compose -f "${DOCKER_COMPOSE_FILE}" logs >&2
        exit 1
    fi
    echo "[*] Waiting for container health (${RETRIES}/${MAX_RETRIES})..."
    sleep "${RETRY_INTERVAL}"
done

echo "[+] LabLink Docker stack is UP and Healthy!"
docker compose -f "${DOCKER_COMPOSE_FILE}" ps
