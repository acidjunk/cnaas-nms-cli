"""Configuration loading for the CNaaS CLI.

Resolves the CNaaS API base URL and bearer token from (in order of precedence):

1. Explicit CLI overrides set via :func:`set_overrides`
2. Process environment variables (``CNAAS_API_KEY``, ``CNAAS_BASE_URL``)
3. A ``.env`` file in the current working directory
4. ``$XDG_CONFIG_HOME/cnaas-cli/.cnaas-cli.env`` (or ``~/.config/cnaas-cli/...``)
5. An interactive prompt (only when stdin is a TTY)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.prompt import Prompt

from .output import console, print_error

CONFIG_DIR_NAME = "cnaas-cli"
CONFIG_FILE_NAME = ".cnaas-cli.env"


def _config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / CONFIG_DIR_NAME


def config_file_path() -> Path:
    """Return the absolute path of the persistent config file."""
    return _config_dir() / CONFIG_FILE_NAME


def _load_dotenv_files() -> None:
    """Load environment variables from `.env` and the user config file (if they exist).

    Existing process env vars always win.
    """
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    cfg = config_file_path()
    if cfg.exists():
        load_dotenv(dotenv_path=cfg, override=False)


class Settings(BaseSettings):
    """CNaaS CLI runtime settings."""

    api_key: SecretStr = Field(default=SecretStr(""), alias="CNAAS_API_KEY")
    base_url: str = Field(default="", alias="CNAAS_BASE_URL")

    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


# Module-level overrides set by the root Typer callback (--api-key / --base-url).
_overrides: dict[str, str] = {}


def set_overrides(api_key: str | None = None, base_url: str | None = None) -> None:
    """Register CLI-flag overrides that take precedence over env/config files."""
    if api_key:
        _overrides["api_key"] = api_key
    if base_url:
        _overrides["base_url"] = base_url


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_settings(interactive: bool = True) -> Settings:
    """Load settings, prompting interactively if required values are missing.

    Raises:
        SystemExit: if a required value is missing in non-interactive mode.
    """
    _load_dotenv_files()
    settings = Settings()

    api_key = _overrides.get("api_key") or settings.api_key.get_secret_value()
    base_url = _overrides.get("base_url") or settings.base_url

    if not base_url:
        if interactive and _is_interactive():
            base_url = Prompt.ask("[cyan]CNaaS base URL[/cyan]", console=console).strip()
        else:
            print_error(
                "Missing CNAAS_BASE_URL. Set it as an environment variable or run "
                "'cnaas auth configure'."
            )
            raise SystemExit(1)

    if not api_key:
        if interactive and _is_interactive():
            api_key = Prompt.ask(
                "[cyan]CNaaS API key[/cyan]", password=True, console=console
            ).strip()
        else:
            print_error(
                "Missing CNAAS_API_KEY. Set it as an environment variable or run "
                "'cnaas auth configure'."
            )
            raise SystemExit(1)

    return Settings(CNAAS_API_KEY=api_key, CNAAS_BASE_URL=base_url)


def save_settings(api_key: str, base_url: str) -> Path:
    """Persist credentials to the user config file. Returns the file path."""
    path = config_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"CNAAS_BASE_URL={base_url}\nCNAAS_API_KEY={api_key}\n",
        encoding="utf-8",
    )
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path
