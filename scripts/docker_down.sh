#!/usr/bin/env bash
# LabLink Docker Compose Stack Shutdown Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="${PROJECT_ROOT}/docker/docker-compose.yml"

echo "=== Stopping LabLink Docker Compose Stack ==="

if command -v docker >/dev/null 2>&1 && [ -f "${DOCKER_COMPOSE_FILE}" ]; then
    echo "[+] Stopping containers while preserving persistent named volumes..."
    docker compose -f "${DOCKER_COMPOSE_FILE}" down
fi

echo "[+] Docker Compose stack stopped cleanly."
