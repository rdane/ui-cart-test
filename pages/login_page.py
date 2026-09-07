"""Handles the two-step (email, then password, then optional TOTP) account.ui.com SSO login form."""
import re

import pyotp
from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def login(self, email: str, password: str, totp_secret: str | None = None) -> None:
        self.page.locator('[data-testid="login-new-user-input"] input').fill(email)
        self.page.locator('[data-testid="login-new-user-submit"]').click()

        password_input = self.page.locator('input[type="password"]')
        password_input.wait_for(state="visible")
        password_input.fill(password)

        # Submit button testid could not be confirmed without a real account;
        # fall back to pressing Enter which submits the form either way.
        submit = self.page.get_by_role("button", name=re.compile("sign in|log in", re.I))
        if submit.count() > 0:
            submit.first.click()
        else:
            password_input.press("Enter")

        self._maybe_handle_totp(totp_secret)

    def _maybe_handle_totp(self, totp_secret: str | None) -> None:
        if not totp_secret:
            return
        # 2FA step is conditional; only acted on if the code input actually appears.
        code_input = self.page.get_by_role("textbox", name=re.compile("code|authentication", re.I))
        try:
            code_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            return
        code_input.fill(pyotp.TOTP(totp_secret).now())
        submit = self.page.get_by_role("button", name=re.compile("verify|submit|continue", re.I))
        if submit.count() > 0:
            submit.first.click()
        else:
            code_input.press("Enter")
