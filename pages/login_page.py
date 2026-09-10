"""Handles the two-step (email, then password, then optional TOTP) account.ui.com SSO login form."""
import time

import pyotp
from playwright.sync_api import Page

_last_totp_code: str | None = None


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def login(self, email: str, password: str, totp_secret: str | None = None) -> None:
        print(f"Logging in as {email}...")
        self._enter_email_or_select_remembered_account(email)

        password_input = self.page.locator('input[type="password"]')
        password_input.wait_for(state="visible")
        password_input.fill(password)
        self.page.locator('[data-testid="login-button"]').click()
        self._maybe_handle_totp(totp_secret)
        self._maybe_dismiss_trust_device_prompt()

    def _enter_email_or_select_remembered_account(self, email: str) -> None:
        # If this browser profile logged in before, /login shows a picker of
        # remembered accounts instead of the plain email form; selecting one
        # goes straight to a combined email+password form.
        remembered_account = self.page.get_by_text(email, exact=False)
        try:
            remembered_account.first.wait_for(state="visible", timeout=5_000)
            remembered_account.first.click()
            return
        except Exception:
            pass
        self.page.locator('[data-testid="login-new-user-input"] input').fill(email)
        self.page.locator('[data-testid="login-new-user-submit"]').click()

    def _maybe_handle_totp(self, totp_secret: str | None) -> None:
        if not totp_secret:
            return
        # MFA step is conditional; six unnamed single-digit boxes, only present
        # when a challenge is issued. Typing into the first distributes the
        # remaining digits across the rest, and the form auto-submits once full.
        code_boxes = self.page.locator('input[autocomplete="one-time-code"]')
        try:
            code_boxes.first.wait_for(state="visible", timeout=10_000)
        except Exception:
            return
        code_boxes.first.click()
        # A per-key delay is required: typed too fast, the site's auto-advance
        # between boxes can't keep up and drops/misplaces digits.
        code_boxes.first.press_sequentially(self._next_totp_code(totp_secret), delay=150)

    def _next_totp_code(self, totp_secret: str) -> str:
        global _last_totp_code
        totp = pyotp.TOTP(totp_secret)
        code = totp.now()
        if code == _last_totp_code:
            # Server rejects a code already used in a prior login this run;
            # block until the next time-step produces a fresh one.
            time.sleep(totp.interval - (time.time() % totp.interval) + 1)
            code = totp.now()
        _last_totp_code = code
        return code

    def _maybe_dismiss_trust_device_prompt(self) -> None:
        # Shown once per new device/browser profile right after a successful MFA check.
        not_now = self.page.get_by_role("button", name="Not now")
        try:
            not_now.wait_for(state="visible", timeout=10_000)
        except Exception:
            return
        not_now.click()
