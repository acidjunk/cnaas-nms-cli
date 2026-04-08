"""Tests for `cnaas repository ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.repository.get_repository_api.sync_detailed",
        FakeResponse.ok({"data": "ok"}),
    )
    result = runner.invoke(cli_app, ["repository", "show", "settings"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == "settings"


def test_refresh(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.repository.put_repository_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["repository", "refresh", "templates"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == "templates"
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["action"] == "refresh"
