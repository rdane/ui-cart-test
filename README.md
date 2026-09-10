# UI Store Cart Persistence Test

Automated Playwright test (Python) that logs into `store.ui.com`, adds a product to the
cart, logs out, logs back in, and verifies the product is still in the cart. Runs inside
Docker for a reproducible environment.

## Prerequisites (Debian)

Install Docker Engine and the Compose plugin:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Add your user to the `docker` group so `docker compose` can be run without `sudo` (log out/in
afterward for it to take effect):

```bash
sudo usermod -aG docker "$USER"
```

Verify:

```bash
docker compose version
```

No local Python, Node, or Playwright install is required — everything runs inside the
container.

## Setup

1. Clone the repository and `cd` into it.
2. Create your local env file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and fill in:
   - `STORE_EMAIL` / `STORE_PASSWORD` — a real store.ui.com account (this test runs against
     the live production site).
   - `TOTP_SECRET` — the authenticator-app secret for that account, if it has 2FA enabled.
     Leave blank if 2FA is disabled.

`.env` is gitignored and never committed.

The product used by the test (`PRODUCT_PATH` / `PRODUCT_NAME`) is a fixed fixture defined as
constants at the top of `tests/test_cart_persistence.py` — edit them there to target a
different product.

## Running the test

Headless (default, works on any machine with Docker, including headless servers/CI):

```bash
docker compose run --rm tests
```

Run with pytest options (e.g. verbose output):

```bash
docker compose run --rm tests pytest -v
```

### Headed mode (watch the browser)

Headed mode renders through the host's native Wayland compositor (no X11/XWayland), so it
requires a Wayland desktop session (e.g. GNOME/KDE on Wayland):

```bash
./scripts/run-headed.sh
```

This fails fast with a clear error if `$WAYLAND_DISPLAY`/`$XDG_RUNTIME_DIR` aren't set (i.e.
you're on X11 or a headless machine) — use headless mode in that case.

### Debugging

Runs the suite paused for a debugger to attach on port 5678 (see `.vscode/launch.json` for
the matching VS Code debug configuration), also headed via Wayland:

```bash
./scripts/run-debug.sh
```

Then start the "Attach" debug configuration in VS Code.

## Test artifacts

On failure, `test-results/` (mounted from the container) contains:
- `test-failed-1.png` — screenshot at the point of failure
- `trace.zip` — full Playwright trace (open with `npx playwright show-trace test-results/.../trace.zip` if Node is available, or inspect via a Playwright trace viewer)
- `video.webm` — screen recording of the run

## Notes

- This test exercises a **real, live account** on production store.ui.com. Cart cleanup is
  handled automatically as part of the test teardown, but leaving the suite mid-failure
  repeatedly can still leave stray items in the account's cart — check manually if in doubt.
- The login flow is Ubiquiti's SSO (`account.ui.com`) and includes handling for MFA
  (TOTP) and the "remembered account" picker shown when the same browser profile/container
  has logged in before within a single run.
