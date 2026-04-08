"""Tests for `cnaas linknets ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list_linknets(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.linknets.get_linknets_api.sync_detailed",
        FakeResponse.ok({"data": {"linknets": [{"id": 1, "device_a": "a", "device_b": "b"}]}}),
    )
    result = runner.invoke(cli_app, ["linknets", "list", "--output", "json"])
    assert result.exit_code == 0
    assert '"device_a"' in result.stdout


def test_show_linknet(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.linknets.get_linknet_by_id_api.sync_detailed",
        FakeResponse.ok({"data": {"id": 7}}),
    )
    result = runner.invoke(cli_app, ["linknets", "show", "7"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == 7


def test_create_linknet(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.linknets.post_linknets_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(
        cli_app,
        ["linknets", "create", "core-01", "core-02", "et-0/0/1", "et-0/0/2", "--ipv4-network", "10.0.0.0/30"],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["device_a"] == "core-01"
    assert body["ipv4_network"] == "10.0.0.0/30"


def test_delete_linknet(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.linknets.delete_linknet_by_id_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["linknets", "delete", "9"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == 9
