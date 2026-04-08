"""Tests for `cnaas devices ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list_devices(runner, cli_app, fake_client, monkeypatch):
    payload = {"status": "success", "data": {"devices": [
        {"id": 1, "hostname": "core-01", "device_type": "CORE", "platform": "junos", "state": "MANAGED"}
    ]}}
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_devices_api.sync_detailed",
        FakeResponse.ok(payload),
    )
    result = runner.invoke(cli_app, ["devices", "list", "--output", "json"])
    assert result.exit_code == 0, result.stdout
    assert "core-01" in result.stdout
    mock.assert_called_once()


def test_list_devices_table(runner, cli_app, fake_client, monkeypatch):
    payload = {"status": "success", "data": {"devices": [
        {"id": 1, "hostname": "core-01", "device_type": "CORE", "platform": "junos", "state": "MANAGED"}
    ]}}
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_devices_api.sync_detailed",
        FakeResponse.ok(payload),
    )
    result = runner.invoke(cli_app, ["devices", "list"])
    assert result.exit_code == 0
    assert "core-01" in result.stdout


def test_show_device(runner, cli_app, fake_client, monkeypatch):
    payload = {"status": "success", "data": {"devices": [{"hostname": "core-01"}]}}
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_device_by_hostname_api.sync_detailed",
        FakeResponse.ok(payload),
    )
    result = runner.invoke(cli_app, ["devices", "show", "core-01"])
    assert result.exit_code == 0
    args, kwargs = mock.call_args
    assert args[0] == "core-01"


def test_create_device(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.post_device_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(
        cli_app,
        ["devices", "create", "core-99", "CORE", "--platform", "eos", "--management-ip", "10.0.0.1"],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"]
    payload = body.to_dict()
    assert payload["hostname"] == "core-99"
    assert payload["device_type"] == "CORE"
    assert payload["platform"] == "eos"
    assert payload["management_ip"] == "10.0.0.1"
    assert "core-99 created" in result.stdout


def test_delete_device(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.delete_device_by_id_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["devices", "delete", "42"])
    assert result.exit_code == 0
    args, kwargs = mock.call_args
    assert args[0] == 42


def test_init_device(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.post_device_init_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(
        cli_app,
        ["devices", "init", "5", "--hostname", "dist-05", "--device-type", "DIST"],
    )
    assert result.exit_code == 0, result.stdout
    args, kwargs = mock.call_args
    assert args[0] == 5
    body = kwargs["body"].to_dict()
    assert body["hostname"] == "dist-05"
    assert body["device_type"] == "DIST"


def test_init_check(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.post_device_init_check_api.sync_detailed",
        FakeResponse.ok({"status": "success", "compatible": True}),
    )
    result = runner.invoke(
        cli_app,
        ["devices", "init-check", "5", "--hostname", "dist-05", "--device-type", "DIST"],
    )
    assert result.exit_code == 0


def test_sync_requires_target(runner, cli_app, fake_client):
    result = runner.invoke(cli_app, ["devices", "sync"])
    assert result.exit_code != 0


def test_sync_devices(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.post_device_sync_api.sync_detailed",
        FakeResponse.ok({"status": "success", "job_id": 123}),
    )
    result = runner.invoke(
        cli_app,
        ["devices", "sync", "--hostname", "core-01", "--dry-run", "--force"],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["hostname"] == "core-01"
    assert body["dry_run"] is True
    assert body["force"] is True


def test_generate_config(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_device_generate_config_api.sync_detailed",
        FakeResponse.ok({"data": {"config": "interface eth0..."}}),
    )
    result = runner.invoke(cli_app, ["devices", "generate-config", "core-01"])
    assert result.exit_code == 0
    assert "interface eth0" in result.stdout


def test_running_config(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_device_running_config_api.sync_detailed",
        FakeResponse.ok({"data": {"config": "running"}}),
    )
    result = runner.invoke(cli_app, ["devices", "running-config", "core-01"])
    assert result.exit_code == 0


def test_devices_error_path(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.devices.get_devices_api.sync_detailed",
        FakeResponse.error(401, "Unauthorized"),
    )
    result = runner.invoke(cli_app, ["devices", "list"])
    assert result.exit_code == 1
