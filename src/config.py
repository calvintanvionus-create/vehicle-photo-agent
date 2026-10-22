"""Reads and checks the four settings from .env."""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The four settings, and nothing else, live in .env.
SETTING_NAMES = ("DISCORD_TOKEN", "CHANNEL_ID", "CLAUDE_MODEL", "DATA_DIR")


class ConfigError(Exception):
    """A setting is missing or wrong. The message names the setting, never its value."""


@dataclass(frozen=True)
class Config:
    discord_token: str = field(repr=False)  # repr=False: the token must never be printed
    channel_id: int
    claude_model: str
    data_dir: Path

    @property
    def photos_dir(self) -> Path:
        return self.data_dir / "photos"


def config_from_mapping(values: Mapping[str, str]) -> Config:
    missing = [name for name in SETTING_NAMES if not (values.get(name) or "").strip()]
    if missing:
        raise ConfigError(
            "Missing settings in .env: " + ", ".join(missing) + ". See .env.example."
        )

    try:
        channel_id = int(values["CHANNEL_ID"].strip())
    except ValueError:
        raise ConfigError("CHANNEL_ID must be a number (digits only).") from None

    return Config(
        discord_token=values["DISCORD_TOKEN"].strip(),
        channel_id=channel_id,
        claude_model=values["CLAUDE_MODEL"].strip(),
        data_dir=Path(values["DATA_DIR"].strip()).expanduser().resolve(),
    )


def load_config() -> Config:
    """Load .env from the project folder, then check the settings."""
    load_dotenv(PROJECT_ROOT / ".env")
    return config_from_mapping(os.environ)
