"""E2E scenario: an item added to the cart survives a logout/login cycle."""
from pages.cart_page import CartPage
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from utils.config import Config


@pytest.fixture(autouse=True)
def empty_cart_after_test(authenticated_page: Page):
    # First iteration of the fixture is run before the test -> nothing is executed before the test, only after.
    yield
    # Cart cleanup is done after the test to ensure repeated runs against the live account start from an empty cart (idempotency)
    cartPage = CartPage(authenticated_page)
    if not cartPage.cart_dialog_is_visible():
        BasePage(authenticated_page).open_cart()
    cartPage.remove_all_items()


@pytest.mark.parametrize("product_path, product_name", [
    ("/products/usw-flex-mini", "Flex Mini"),
])
def test_product_persists_in_cart_after_relogin(
    authenticated_page: Page, config: Config, product_path: str, product_name: str
):
    page = authenticated_page
    base = BasePage(page)

    base.assert_cart_is_empty()

    ProductPage(page).goto(config.base_url, product_path)
    ProductPage(page).add_to_cart()

    cart = base.open_cart()
    cart.assert_contains_product(product_name)
    cart.close()

    base.logout()
    base.go_to_sign_in()
    LoginPage(page).login(config.email, config.password, config.totp_secret)
    page.wait_for_url(f"{config.base_url}**")

    cart = base.open_cart()
    cart.assert_contains_product(product_name)
