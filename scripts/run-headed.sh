#!/usr/bin/env bash
# Runs the Dockerized Playwright tests in headed mode using Chromium's native
# Ozone/Wayland backend, forwarding the host compositor socket directly
# (no XWayland/X11 involved).
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

# DISPLAY is set to a dummy value: only satisfies Playwright's own X-server preflight check, unused by Chromium's Ozone/Wayland backend.

docker compose run --rm --build \
  -e HEADLESS=false \
  -e PW_WAYLAND=1 \
  -e WAYLAND_DISPLAY="$WAYLAND_DISPLAY" \
  -e XDG_RUNTIME_DIR=/tmp/wayland-runtime \
  -e DISPLAY=:0 \
  -v "$SOCKET_PATH:/tmp/wayland-runtime/$WAYLAND_DISPLAY" \
  tests "$@"
