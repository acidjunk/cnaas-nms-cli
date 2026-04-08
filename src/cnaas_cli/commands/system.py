"""`cnaas system ...` — system-level CNaaS operations."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.system import get_version_api, post_shutdown_api

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json, print_success

app = typer.Typer(help="System-level CNaaS operations.", no_args_is_help=True)


@app.command("version")
def version() -> None:
    """Show the CNaaS server version."""
    client = build_client()
    with handle_api_call("get system version"):
        response = get_version_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("shutdown")
def shutdown(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt."),
) -> None:
    """Gracefully shut down the CNaaS API server (admin only)."""
    if not confirm:
        typer.confirm("This will shut down the CNaaS API server. Continue?", abort=True)
    client = build_client()
    with handle_api_call("shutdown CNaaS server"):
        response = post_shutdown_api.sync_detailed(client=client)
        parse_response(response)
    print_success("Shutdown requested.")
