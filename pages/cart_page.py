"""The 'Your Cart' dialog: assertions and cleanup helpers."""
from playwright.sync_api import Page, expect


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog", name="Your Cart")

    def assert_contains_product(self, product_name: str) -> None:
        expect(self.dialog.get_by_text(product_name, exact=False)).to_be_visible()

    def close(self) -> None:
        self.dialog.get_by_role("button", name="Close").click()

    def remove_all_items(self) -> None:
        # Used as test teardown so repeated runs against the live account
        # start from an empty cart (idempotency).
        remove_buttons = self.dialog.get_by_role("button", name="Remove")
        while remove_buttons.count() > 0:
            remove_buttons.first.click()
        expect(self.dialog.get_by_text("Your cart is empty")).to_be_visible()
