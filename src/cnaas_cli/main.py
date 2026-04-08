"""Root Typer application for the CNaaS CLI."""

from __future__ import annotations

import typer

from . import __version__
from .commands import (
    auth,
    devices,
    firmware,
    groups,
    interfaces,
    jobs,
    linknets,
    mgmtdomains,
    repository,
    system,
)
from .commands import (
    settings as settings_cmd,
)
from .config import set_overrides
from .output import console

app = typer.Typer(
    name="cnaas",
    help="A modern CLI for managing a CNaaS-NMS deployment.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.add_typer(devices.app, name="devices")
app.add_typer(linknets.app, name="linknets")
app.add_typer(mgmtdomains.app, name="mgmtdomains")
app.add_typer(groups.app, name="groups")
app.add_typer(interfaces.app, name="interfaces")
app.add_typer(firmware.app, name="firmware")
app.add_typer(jobs.app, name="jobs")
app.add_typer(repository.app, name="repository")
app.add_typer(settings_cmd.app, name="settings")
app.add_typer(system.app, name="system")
app.add_typer(auth.app, name="auth")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"cnaas-nms-cli [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback()
def _root(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show the CLI version and exit.",
    ),
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="CNAAS_API_KEY_OVERRIDE",
        help="Override the CNaaS API key (takes precedence over CNAAS_API_KEY).",
    ),
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        envvar="CNAAS_BASE_URL_OVERRIDE",
        help="Override the CNaaS base URL (takes precedence over CNAAS_BASE_URL).",
    ),
) -> None:
    """Global options applied to every subcommand."""
    set_overrides(api_key=api_key, base_url=base_url)


if __name__ == "__main__":
    app()
