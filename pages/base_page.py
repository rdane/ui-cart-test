"""Common page interactions shared across all store.ui.com pages."""
import re

from playwright.sync_api import Page
from pages.cart_page import CartPage


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def dismiss_cookie_banner(self) -> None:
        # Reappears on later navigations too (not just the first visit), and
        # its backdrop can block unrelated clicks until dismissed.
        button = self.page.get_by_role("button", name="Accept All Cookies")
        try:
            button.click(timeout=5_000)
        except Exception:
            pass

    def open_account_menu(self) -> None:
        # Accessible name is "Account Menu" when logged out, but becomes a
        # numeric badge once logged in; this data attribute is stable in both states.
        self.page.locator('[data-uic-component="Account.Trigger"]').click()

    def go_to_sign_in(self) -> None:
        self.open_account_menu()
        self.page.get_by_role("link", name="Sign in").click()

    def open_cart(self) -> CartPage:

        self.dismiss_cookie_banner()
        # The cart badge is a leaf element showing a bare digit; the
        # account-menu trigger also renders an unrelated numeric badge, so
        # it's explicitly excluded here rather than guessed by tag/order.
        # Polls (rather than a one-shot check) since the badge renders
        # asynchronously right after add-to-cart.
        self.page.wait_for_function(
            """() => {
                const badge = Array.from(document.querySelectorAll('header *')).find(el =>
                    el.children.length === 0 &&
                    /^\\d+$/.test(el.textContent.trim()) &&
                    !el.closest('[data-uic-component="Account.Trigger"]')
                );
                if (badge) { badge.setAttribute('data-qa-cart-badge', 'true'); return true; }
                return false;
            }"""
        )
        self.page.locator('[data-qa-cart-badge="true"]').click()
        return CartPage(self.page)

    def logout(self) -> None:
        # NOTE: exact "Sign out" label/flow could not be verified without a
        # real account during exploration; adjust if the live site differs.
        self.open_account_menu()
        self.page.get_by_role("link", name=re.compile("sign out", re.I)).click()
