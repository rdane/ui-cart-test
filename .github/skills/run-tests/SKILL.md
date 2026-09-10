---
name: run-tests
description: 'Run the Dockerized Playwright test suite for the ui-store-shop-cart-test project (headless, headed, or debug). Use when asked to run/execute the tests, check if the suite passes, view failure artifacts, or debug a failing test.'
---

# Run Tests

Tests run entirely inside Docker (via `docker compose`) — no local Python/Node/Playwright
install is required or expected. Never run `pytest` directly on the host.

## Prerequisites

1. Docker Engine + Compose plugin installed (`docker compose version` to check; see
   README.md for install steps if missing).
2. A `.env` file in the repo root (gitignored, never commit it):
   ```bash
   cp .env.example .env
   ```
   Fill in:
   - `STORE_EMAIL` / `STORE_PASSWORD` — a real store.ui.com account. **This suite exercises
     the live production site**, not a mock/staging environment.
   - `TOTP_SECRET` — authenticator-app secret, only if the account has 2FA enabled.

   `PRODUCT_PATH` / `PRODUCT_NAME` are not `.env` vars — they're fixed fixture constants at
   the top of `tests/test_cart_persistence.py`; edit them there to target a different product.

   If `.env` is missing or a required var is unset, `utils/config.py` raises
   `RuntimeError: Required environment variable ... is not set` at collection time — that's
   the expected failure mode, not a bug to fix.

## Running

**Headless (default — works anywhere, including CI/headless servers):**
```bash
docker compose run --rm tests
```

**With pytest options** (e.g. verbose, run a specific test):
```bash
docker compose run --rm tests pytest -v
docker compose run --rm tests pytest -v tests/test_cart_persistence.py::test_product_persists_in_cart_after_relogin
```

**Headed (watch the browser):** requires a Wayland desktop session — fails fast with a
clear error on X11 or headless machines. Renders through the host compositor directly
(no XWayland):
```bash
./scripts/run-headed.sh
```

**Debug (paused for a debugger on port 5678):** also headed via Wayland. Start VS Code's
"Attach" debug configuration (`.vscode/launch.json`) after launching:
```bash
./scripts/run-debug.sh
```

## After a run

- Exit code `0` — suite passed.
- On failure, check `test-results/` (mounted from the container):
  - `test-failed-1.png` — screenshot at point of failure
  - `trace.zip` — full Playwright trace (`npx playwright show-trace test-results/.../trace.zip`
    if Node is available, or use a Playwright trace viewer)
  - `video.webm` — screen recording of the run
- Cart cleanup runs as test teardown (`empty_cart_after_test` fixture in
  `tests/test_cart_persistence.py`) so repeated runs start from an empty cart. Repeated
  mid-run failures can still leave stray items — check the live account manually if a test
  behaves as though the cart wasn't actually empty.
