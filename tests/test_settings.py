"""Tests for `cnaas settings ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.settings.get_settings_api.sync_detailed",
        FakeResponse.ok({"data": {}}),
    )
    result = runner.invoke(cli_app, ["settings", "show", "--hostname", "core-01"])
    assert result.exit_code == 0
    assert mock.call_args.kwargs["hostname"] == "core-01"


def test_model(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.settings.get_settings_model_api.sync_detailed",
        FakeResponse.ok({"data": {}}),
    )
    result = runner.invoke(cli_app, ["settings", "model"])
    assert result.exit_code == 0


def test_server(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.settings.get_settings_server_ap_i.sync_detailed",
        FakeResponse.ok({"data": {}}),
    )
    result = runner.invoke(cli_app, ["settings", "server"])
    assert result.exit_code == 0
