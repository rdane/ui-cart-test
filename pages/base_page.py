"""Common page interactions shared across all store.ui.com pages."""
import re

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def dismiss_cookie_banner(self) -> None:
        # Banner only appears on first visit per session; ignore if absent.
        button = self.page.get_by_role("button", name="Accept All Cookies")
        try:
            button.click(timeout=5_000)
        except Exception:
            pass

    def open_account_menu(self) -> None:
        self.page.get_by_role("button", name="Account Menu").click()

    def go_to_sign_in(self) -> None:
        self.open_account_menu()
        self.page.get_by_role("link", name="Sign in").click()

    def open_cart(self) -> "CartPage":
        from pages.cart_page import CartPage

        # The cart trigger has no accessible name; it's identified by the
        # numeric quantity badge rendered inside the page header.
        self.page.locator("header").get_by_text(re.compile(r"^\d+$")).first.click()
        return CartPage(self.page)

    def logout(self) -> None:
        # NOTE: exact "Sign out" label/flow could not be verified without a
        # real account during exploration; adjust if the live site differs.
        self.open_account_menu()
        self.page.get_by_role("link", name=re.compile("sign out", re.I)).click()
