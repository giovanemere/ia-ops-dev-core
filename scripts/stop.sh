#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "⏹️  Stopping IA-Ops Dev Core Services..."
cd "$PROJECT_DIR/docker"
docker compose down

echo "✅ Services stopped"
