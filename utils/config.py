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
    headless: bool
    totp_secret: str | None


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
        headless=os.getenv("HEADLESS", "true").lower() != "false",
        totp_secret=os.getenv("TOTP_SECRET") or None,
    )
