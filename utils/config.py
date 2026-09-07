"""Loads test configuration from environment variables / .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    base_url: str
    email: str
    password: str
    product_path: str
    product_name: str
    headless: bool


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is not set (see .env.example)")
    return value


def load_config() -> Config:
    return Config(
        base_url=os.getenv("BASE_URL", "https://store.ui.com/us/en").rstrip("/"),
        email=_require("STORE_EMAIL"),
        password=_require("STORE_PASSWORD"),
        product_path=os.getenv("PRODUCT_PATH", "/products/usw-flex-mini"),
        product_name=os.getenv("PRODUCT_NAME", "Flex Mini"),
        headless=os.getenv("HEADLESS", "true").lower() != "false",
    )
