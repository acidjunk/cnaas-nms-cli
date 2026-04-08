"""Tests for `cnaas auth ...`."""

from __future__ import annotations

from cnaas_cli.config import config_file_path

from .conftest import FakeResponse, stub_endpoint


def test_whoami(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.auth.get_identity_api.sync_detailed",
        FakeResponse.ok({"data": {"username": "alice"}}),
    )
    result = runner.invoke(cli_app, ["auth", "whoami"])
    assert result.exit_code == 0
    assert "alice" in result.stdout


def test_permissions(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.auth.get_permissions_api.sync_detailed",
        FakeResponse.ok({"data": {"perms": []}}),
    )
    result = runner.invoke(cli_app, ["auth", "permissions"])
    assert result.exit_code == 0


def test_refresh(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.auth.post_refresh_api.sync_detailed",
        FakeResponse.ok({"data": {"token": "new-token"}}),
    )
    result = runner.invoke(cli_app, ["auth", "refresh"])
    assert result.exit_code == 0
    assert "Token refreshed" in result.stdout


def test_configure_writes_file(runner, cli_app):
    result = runner.invoke(
        cli_app,
        [
            "auth", "configure",
            "--base-url", "https://saved.example/api/v1.0",
            "--api-key", "saved-token",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert config_file_path().exists()
    contents = config_file_path().read_text()
    assert "saved-token" in contents
    assert "saved.example" in contents


def test_config_path(runner, cli_app):
    result = runner.invoke(cli_app, ["auth", "config-path"])
    assert result.exit_code == 0
