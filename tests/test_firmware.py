"""Tests for `cnaas firmware ...`."""

from __future__ import annotations

from .conftest import FakeResponse, stub_endpoint


def test_list(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.get_firmware_api.sync_detailed",
        FakeResponse.ok({"data": {"files": []}}),
    )
    result = runner.invoke(cli_app, ["firmware", "list"])
    assert result.exit_code == 0


def test_show(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.get_firmware_image_api.sync_detailed",
        FakeResponse.ok({"data": {"filename": "junos.tgz"}}),
    )
    result = runner.invoke(cli_app, ["firmware", "show", "junos.tgz"])
    assert result.exit_code == 0
    assert mock.call_args.args[0] == "junos.tgz"


def test_download(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.post_firmware_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(
        cli_app,
        [
            "firmware", "download",
            "--url", "https://example.test/junos.tgz",
            "--checksum", "abc123",
            "--algorithm", "sha256",
            "--filename", "junos.tgz",
        ],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["url"] == "https://example.test/junos.tgz"
    assert body["checksum"] == {"algorithm": "sha256", "checksum": "abc123"}
    assert body["filename"] == "junos.tgz"


def test_delete(runner, cli_app, fake_client, monkeypatch):
    stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.delete_firmware_image_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["firmware", "delete", "junos.tgz"])
    assert result.exit_code == 0


def test_upgrade(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.post_firmware_upgrade_api.sync_detailed",
        FakeResponse.ok({"status": "success", "job_id": 7}),
    )
    result = runner.invoke(
        cli_app,
        [
            "firmware", "upgrade",
            "--url", "https://example.test/junos.tgz",
            "--group", "core",
            "--reboot",
        ],
    )
    assert result.exit_code == 0, result.stdout
    body = mock.call_args.kwargs["body"].to_dict()
    assert body["url"] == "https://example.test/junos.tgz"
    assert body["group"] == "core"
    assert body["reboot"] is True


def test_upgrade_requires_target(runner, cli_app, fake_client):
    result = runner.invoke(cli_app, ["firmware", "upgrade", "--url", "https://example.test/junos.tgz"])
    assert result.exit_code != 0


def test_set_default(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.post_firmware_set_default_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["firmware", "set-default", "junos.tgz"])
    assert result.exit_code == 0, result.stdout
    assert mock.call_args.args[0] == "junos.tgz"


def test_upgrade_check(runner, cli_app, fake_client, monkeypatch):
    mock = stub_endpoint(
        monkeypatch,
        "cnaas_cli.commands.firmware.post_firmware_upgradecheck_api.sync_detailed",
        FakeResponse.ok({"status": "success"}),
    )
    result = runner.invoke(cli_app, ["firmware", "upgrade-check", "--group", "core"])
    assert result.exit_code == 0, result.stdout
    assert mock.call_args.kwargs["body"].to_dict()["group"] == "core"


def test_upgrade_check_requires_group(runner, cli_app, fake_client):
    result = runner.invoke(cli_app, ["firmware", "upgrade-check"])
    assert result.exit_code != 0
