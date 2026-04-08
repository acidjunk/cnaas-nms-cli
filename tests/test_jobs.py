"""Tests for `cnaas jobs ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.jobs.get_jobs_api.sync_detailed",
        FakeResponse.ok({"data": {"jobs": [{"id": 1, "status": "FINISHED", "function_name": "sync"}]}}),
    )
    result = runner.invoke(cli_app, ["jobs", "list", "--output", "json"])
    assert result.exit_code == 0
    assert "FINISHED" in result.stdout


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.jobs.get_job_by_id_api.sync_detailed",
        FakeResponse.ok({"data": {"id": 42, "status": "RUNNING"}}),
    )
    result = runner.invoke(cli_app, ["jobs", "show", "42"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == 42


def test_abort(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.jobs.put_job_by_id_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["jobs", "abort", "42"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == 42
