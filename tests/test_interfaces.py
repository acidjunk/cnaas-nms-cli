"""Tests for `cnaas interfaces ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.interfaces.get_interface_api.sync_detailed",
        FakeResponse.ok({"data": {"interfaces": []}}),
    )
    result = runner.invoke(cli_app, ["interfaces", "list", "core-01"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == "core-01"


def test_status(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.interfaces.get_interface_status_api.sync_detailed",
        FakeResponse.ok({"data": {"status": []}}),
    )
    result = runner.invoke(cli_app, ["interfaces", "status", "core-01"])
    assert result.exit_code == 0


def test_set_status(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.interfaces.put_interface_status_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["interfaces", "set-status", "core-01"])
    assert result.exit_code == 0
