"""E2E scenario: an item added to the cart survives a logout/login cycle."""
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from utils.config import Config


@pytest.fixture(autouse=True)
def empty_cart_after_test(authenticated_page: Page):
    yield
    # Keep the live account's cart empty regardless of test outcome.
    BasePage(authenticated_page).open_cart().remove_all_items()


def test_product_persists_in_cart_after_relogin(authenticated_page: Page, config: Config):
    page = authenticated_page
    base = BasePage(page)

    ProductPage(page).goto(config.base_url, config.product_path)
    ProductPage(page).add_to_cart()

    cart = base.open_cart()
    cart.assert_contains_product(config.product_name)
    cart.close()

    base.logout()
    base.go_to_sign_in()
    LoginPage(page).login(config.email, config.password)
    page.wait_for_url(f"{config.base_url}**")

    cart = base.open_cart()
    cart.assert_contains_product(config.product_name)
