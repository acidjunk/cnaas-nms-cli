"""Tests for `cnaas system ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_version(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.system.get_version_api.sync_detailed",
        FakeResponse.ok({"data": {"version": "1.6.0"}}),
    )
    result = runner.invoke(cli_app, ["system", "version"])
    assert result.exit_code == 0
    assert "1.6.0" in result.stdout


def test_shutdown_confirmed(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.system.post_shutdown_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["system", "shutdown", "--yes"])
    assert result.exit_code == 0


def test_shutdown_aborted(runner, cli_app, fake_client):
    result = runner.invoke(cli_app, ["system", "shutdown"], input="n\n")
    assert result.exit_code != 0
