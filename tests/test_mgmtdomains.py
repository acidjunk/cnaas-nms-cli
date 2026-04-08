"""Tests for `cnaas mgmtdomains ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.mgmtdomains.get_mgmtdomains_api.sync_detailed",
        FakeResponse.ok({"data": {"mgmtdomains": [{"id": 1, "device_a": "a", "device_b": "b", "vlan": 10}]}}),
    )
    result = runner.invoke(cli_app, ["mgmtdomains", "list", "--output", "json"])
    assert result.exit_code == 0


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.mgmtdomains.get_mgmtdomain_by_id_api.sync_detailed",
        FakeResponse.ok({"data": {"id": 3}}),
    )
    result = runner.invoke(cli_app, ["mgmtdomains", "show", "3"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == 3


def test_create(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.mgmtdomains.post_mgmtdomains_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(
        cli_app,
        [
            "mgmtdomains", "create",
            "core-01", "core-02", "10",
            "10.0.0.1/24", "fd00::1/64",
            "--description", "primary",
        ],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["vlan"] == 10
    assert body["description"] == "primary"


def test_delete(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.mgmtdomains.delete_mgmtdomain_by_id_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["mgmtdomains", "delete", "3"])
    assert result.exit_code == 0
