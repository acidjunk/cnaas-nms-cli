"""Tests for cnaas_cli.config."""

from __future__ import annotations

import pytest

from cnaas_cli.config import (
    config_file_path,
    get_settings,
    save_settings,
    set_overrides,
)


def test_env_loading():
    settings = get_settings()
    assert settings.base_url == "https://cnaas.example.test/api/v1.0"
    assert settings.api_key.get_secret_value() == "test-token"


def test_overrides_take_precedence():
    set_overrides(api_key="override-key", base_url="https://override.example/api/v1.0")
    settings = get_settings()
    assert settings.base_url == "https://override.example/api/v1.0"
    assert settings.api_key.get_secret_value() == "override-key"


def test_save_and_load(monkeypatch, tmp_path):
    monkeypatch.delenv("CNAAS_BASE_URL", raising=False)
    monkeypatch.delenv("CNAAS_API_KEY", raising=False)
    path = save_settings(api_key="saved-key", base_url="https://saved.example/api/v1.0")
    assert path.exists()
    assert path == config_file_path()
    settings = get_settings()
    assert settings.base_url == "https://saved.example/api/v1.0"
    assert settings.api_key.get_secret_value() == "saved-key"


def test_missing_non_interactive(monkeypatch):
    monkeypatch.delenv("CNAAS_BASE_URL", raising=False)
    monkeypatch.delenv("CNAAS_API_KEY", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    with pytest.raises(SystemExit):
        get_settings()
