"""Tests for `cnaas groups ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.groups.get_groups_api.sync_detailed",
        FakeResponse.ok({"data": {"groups": ["core", "dist"]}}),
    )
    result = runner.invoke(cli_app, ["groups", "list"])
    assert result.exit_code == 0
    assert "core" in result.stdout


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.groups.get_groups_api_by_name.sync_detailed",
        FakeResponse.ok({"data": {"members": ["core-01"]}}),
    )
    result = runner.invoke(cli_app, ["groups", "show", "core"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == "core"


def test_os_version(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.groups.get_groups_api_by_name_osversion.sync_detailed",
        FakeResponse.ok({"data": {"22.4R3": 5}}),
    )
    result = runner.invoke(cli_app, ["groups", "os-version", "core"])
    assert result.exit_code == 0
