"""Shared pytest fixtures: config loading and pre-authenticated page setup."""
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.login_page import LoginPage
from utils.config import Config, load_config


@pytest.fixture(scope="session")
def config() -> Config:
    return load_config()


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1440, "height": 900}}


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, config: Config):
    return {**browser_type_launch_args, "headless": config.headless}


@pytest.fixture
def authenticated_page(page: Page, config: Config) -> Page:
    page.goto(config.base_url)
    base = BasePage(page)
    base.dismiss_cookie_banner()
    base.go_to_sign_in()
    LoginPage(page).login(config.email, config.password, config.totp_secret)
    page.wait_for_url(f"{config.base_url}**")
    return page
