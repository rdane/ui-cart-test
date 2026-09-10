"""Common page interactions shared across all store.ui.com pages."""
import re

from playwright.sync_api import Page, expect
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
        self.page.locator('[data-uic-component="Account.Trigger"]').click()

    def go_to_sign_in(self) -> None:
        print("Navigating to sign in...")
        self.open_account_menu()
        self.page.get_by_role("link", name="Sign in").click()

    def open_cart(self) -> CartPage:

        self.dismiss_cookie_banner()
        # The cart badge is a leaf element showing a bare digit; the
        # account-menu trigger also renders an unrelated numeric badge, so
        # it's explicitly excluded here rather than guessed by tag/order.
        # Polled from Python (rather than wait_for_function's in-page polling loop):
        # this site's CSP disallows 'unsafe-eval', which the in-page loop hits on its
        # later iterations (only ever-first-tick evaluate() calls are reliable here).
        find_badge = """() => {
            const badge = Array.from(document.querySelectorAll('header *')).find(el =>
                el.children.length === 0 &&
                /^\\d+$/.test(el.textContent.trim()) &&
                !el.closest('[data-uic-component="Account.Trigger"]')
            );
            if (badge) { badge.setAttribute('data-qa-cart-badge', 'true'); return true; }
            return false;
        }"""
        found = False
        for _ in range(40):
            if self.page.evaluate(find_badge):
                found = True
                break
            self.page.wait_for_timeout(250)
        assert found, "Could not find the cart badge in the header"
        self.page.locator('[data-qa-cart-badge="true"]').click()
        return CartPage(self.page)

    def assert_cart_is_empty(self) -> None:
        print("Asserting cart is empty...")
        # No badge means open_cart() has nothing to click, so this checks the header's
        # own "Your cart is empty" tooltip instead of trying to open the cart dialog.
        # The cart icon has no data-uic-component/aria-label of its own, and its
        # position among header icons shifts between guest/authenticated states, so
        # it's found by its mask-image (cartEmpty.svg) like open_cart tags the badge.
        # Polled from Python (rather than wait_for_function's in-page polling loop):
        # this site's CSP disallows 'unsafe-eval', which the in-page loop hits on its
        # later iterations; a plain evaluate() call doesn't need it and works reliably.
        find_icon = """() => {
            const icon = Array.from(document.querySelectorAll('header *')).find(el => {
                const mask = getComputedStyle(el).maskImage || getComputedStyle(el).webkitMaskImage || '';
                return mask.indexOf('/cart') !== -1;
            });
            if (icon) { icon.setAttribute('data-qa-cart-icon', 'true'); return true; }
            return false;
        }"""
        found = False
        for _ in range(20):
            if self.page.evaluate(find_icon):
                found = True
                break
            self.page.wait_for_timeout(250)
        assert found, "Could not find the cart icon in the header"
        self.page.locator('[data-qa-cart-icon="true"]').hover()
        expect(self.page.get_by_role("tooltip", name="Your cart is empty")).to_be_visible()

    def logout(self) -> None:
        print("Logging out...")
        self.open_account_menu()
        self.page.get_by_role("link", name="Sign out").click()
