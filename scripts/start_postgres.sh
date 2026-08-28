#!/usr/bin/env bash
# LabLink Docker PostgreSQL Container Startup Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose.yml"

echo "=== Starting PostgreSQL Service via Docker Compose ==="

if ! command -v docker >/dev/null 2>&1; then
    echo "[!] Warning: docker binary not found on PATH. Assuming local PostgreSQL instance is running."
    exit 0
fi

if [ -f "${DOCKER_COMPOSE_FILE}" ]; then
    echo "[+] Starting postgres container from docker/docker-compose.yml..."
    docker compose -f "${DOCKER_COMPOSE_FILE}" up -d postgres 2>/dev/null || docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d postgres 2>/dev/null || {
        echo "[!] Notice: Unable to connect to Docker daemon. Using active PostgreSQL service on localhost:5432."
    }
else
    echo "[-] Error: docker/docker-compose.yml not found at ${DOCKER_COMPOSE_FILE}" >&2
    exit 1
fi
