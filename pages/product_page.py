"""Product detail page: navigation and add-to-cart action."""
from playwright.sync_api import Page, expect


class ProductPage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, base_url: str, product_path: str) -> None:
        self.page.goto(f"{base_url}{product_path}")

    def add_to_cart(self) -> None:
        button = self.page.get_by_role("button", name="Add to Cart")
        button.click()
        # Button becomes disabled once the item is in the cart, confirming success.
        expect(button).to_be_disabled()
