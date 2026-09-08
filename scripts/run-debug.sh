#!/usr/bin/env bash
# Runs the Dockerized tests paused for a VS Code debugger to attach on port
# 5678 (see .vscode/launch.json), rendering headed via the host's native
# Wayland compositor (forwarded socket).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ -z "${WAYLAND_DISPLAY:-}" ] || [ -z "${XDG_RUNTIME_DIR:-}" ]; then
  echo "error: \$WAYLAND_DISPLAY / \$XDG_RUNTIME_DIR are not set — this doesn't look like a Wayland session." >&2
  exit 1
fi

SOCKET_PATH="$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"
if [ ! -S "$SOCKET_PATH" ]; then
  echo "error: Wayland socket not found at $SOCKET_PATH" >&2
  exit 1
fi

echo "Waiting for the VS Code debugger to attach on localhost:5678 ..." >&2

docker compose run --rm --build \
  -p 127.0.0.1:5678:5678 \
  -e HEADLESS=false \
  -e PW_WAYLAND=1 \
  -e WAYLAND_DISPLAY="$WAYLAND_DISPLAY" \
  -e XDG_RUNTIME_DIR=/tmp/wayland-runtime \
  -e DISPLAY=:0 `# dummy value: only satisfies Playwright's own X-server preflight check` \
  -v "$SOCKET_PATH:/tmp/wayland-runtime/$WAYLAND_DISPLAY" \
  tests \
  python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m pytest "$@"

