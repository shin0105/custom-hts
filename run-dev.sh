#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
PID_DIR="$ROOT_DIR/.dev-pids"

mkdir -p "$PID_DIR"

start_backend() {
  cd "$BACKEND_DIR"
  uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
}

start_frontend() {
  cd "$FRONTEND_DIR"
  npm run dev
}

start_backend &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_DIR/backend.pid"

start_frontend &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PID_DIR/frontend.pid"

cleanup() {
  rm -f "$PID_DIR/backend.pid" "$PID_DIR/frontend.pid" 2>/dev/null || true
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

wait "$BACKEND_PID" "$FRONTEND_PID"
