#!/usr/bin/env bash
# LabLink CI/CD Resource Cleanup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="${SCRIPT_DIR}/.api.pid"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose.yml"

echo "=== Cleaning Up CI/CD Services and Resources ==="

# 1. Terminate background API process if PID file exists
if [ -f "${PID_FILE}" ]; then
    API_PID="$(cat "${PID_FILE}")"
    if kill -0 "${API_PID}" 2>/dev/null; then
        echo "[+] Terminating API server process (PID: ${API_PID})..."
        kill -15 "${API_PID}" 2>/dev/null || kill -9 "${API_PID}" 2>/dev/null || true
    fi
    rm -f "${PID_FILE}"
fi

# 2. Stop Docker Compose containers if docker is available
if command -v docker >/dev/null 2>&1 && [ -f "${DOCKER_COMPOSE_FILE}" ]; then
    echo "[+] Stopping Docker Compose services..."
    docker compose -f "${DOCKER_COMPOSE_FILE}" stop postgres 2>/dev/null || true
fi

echo "[+] Cleanup complete."
