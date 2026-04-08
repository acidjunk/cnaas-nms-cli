"""Tests for the root Typer app."""

from __future__ import annotations

from cnaas_cli import __version__


def test_help(runner, cli_app):
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "A modern CLI for managing a CNaaS-NMS deployment." in result.stdout
    for group in [
        "devices",
        "linknets",
        "mgmtdomains",
        "groups",
        "interfaces",
        "firmware",
        "jobs",
        "repository",
        "settings",
        "system",
        "auth",
    ]:
        assert group in result.stdout


def test_version(runner, cli_app):
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_subcommand_help(runner, cli_app):
    for group in ["devices", "linknets", "firmware", "jobs", "system", "auth"]:
        result = runner.invoke(cli_app, [group, "--help"])
        assert result.exit_code == 0, f"{group} --help failed: {result.stdout}"


def test_missing_config_non_interactive(runner, cli_app, monkeypatch):
    """Without env vars and without a TTY, the CLI should fail with a helpful error."""
    monkeypatch.delenv("CNAAS_BASE_URL", raising=False)
    monkeypatch.delenv("CNAAS_API_KEY", raising=False)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    result = runner.invoke(cli_app, ["system", "version"])
    assert result.exit_code == 1
