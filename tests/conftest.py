"""Shared test fixtures.

We never make a real HTTP call. Instead, every test stubs the per-endpoint
``sync_detailed`` function (the generated client returns a Response-like object
whose ``content`` is the raw JSON body — that's exactly what
:func:`cnaas_cli.errors.parse_response` expects).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from cnaas_cli import client as client_module
from cnaas_cli import config as config_module
from cnaas_cli.main import app


@dataclass
class FakeResponse:
    """Mimics the bits of cnaas-nms-api-client's Response[Any] our code touches."""

    status_code: int = 200
    content: bytes = b"{}"
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def ok(cls, payload: Any) -> FakeResponse:
        return cls(status_code=200, content=json.dumps(payload).encode("utf-8"))

    @classmethod
    def error(cls, status: int, message: str | list[str]) -> FakeResponse:
        return cls(status_code=status, content=json.dumps({"message": message}).encode("utf-8"))


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cli_app():
    return app


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path):
    """Provide deterministic, isolated config for every test."""
    monkeypatch.setenv("CNAAS_BASE_URL", "https://cnaas.example.test/api/v1.0")
    monkeypatch.setenv("CNAAS_API_KEY", "test-token")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    # Reset overrides and the cached AuthenticatedClient between tests.
    config_module._overrides.clear()
    client_module._cached_client.cache_clear()
    yield
    config_module._overrides.clear()
    client_module._cached_client.cache_clear()


@pytest.fixture
def fake_client(monkeypatch):
    """Replace cnaas_cli.client.build_client with a MagicMock factory."""
    mock_client = MagicMock(name="AuthenticatedClient")
    monkeypatch.setattr("cnaas_cli.client.build_client", lambda *a, **kw: mock_client)
    # Also patch the symbol re-imported into each commands module.
    for mod in (
        "cnaas_cli.commands.devices",
        "cnaas_cli.commands.linknets",
        "cnaas_cli.commands.mgmtdomains",
        "cnaas_cli.commands.groups",
        "cnaas_cli.commands.interfaces",
        "cnaas_cli.commands.firmware",
        "cnaas_cli.commands.jobs",
        "cnaas_cli.commands.repository",
        "cnaas_cli.commands.settings",
        "cnaas_cli.commands.system",
        "cnaas_cli.commands.auth",
    ):
        monkeypatch.setattr(f"{mod}.build_client", lambda *a, **kw: mock_client)
    return mock_client


def stub_endpoint(monkeypatch, dotted_path: str, response: FakeResponse) -> MagicMock:
    """Replace a generated `sync_detailed` with a MagicMock returning `response`."""
    mock = MagicMock(return_value=response)
    monkeypatch.setattr(dotted_path, mock)
    return mock
