"""Handles the two-step (email, then password) account.ui.com SSO login form."""
import re

from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def login(self, email: str, password: str) -> None:
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
