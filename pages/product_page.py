"""Product detail page: navigation and add-to-cart action."""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductPage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, base_url: str, product_path: str) -> None:
        print(f"Navigating to product page: {product_path}")
        self.page.goto(f"{base_url}{product_path}")
        BasePage(self.page).dismiss_cookie_banner()

    def add_to_cart(self) -> None:
        print("Adding product to cart...")
        button = self.page.get_by_role("button", name="Add to Cart")
        button.click()
