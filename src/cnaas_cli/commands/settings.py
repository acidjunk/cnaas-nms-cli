"""`cnaas settings ...` — query CNaaS settings."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.settings import (
    get_settings_api,
    get_settings_model_api,
    get_settings_server_ap_i,
)
from cnaas_nms_api_client.types import UNSET

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json

app = typer.Typer(help="Inspect CNaaS settings.", no_args_is_help=True)


@app.command("show")
def show_settings(
    hostname: str | None = typer.Option(None, help="Filter settings by hostname."),
    device_type: str | None = typer.Option(None, help="Filter settings by device type."),
) -> None:
    """Show effective CNaaS settings, optionally filtered by hostname or device type."""
    client = build_client()
    with handle_api_call("show settings"):
        response = get_settings_api.sync_detailed(
            client=client,
            hostname=hostname or UNSET,
            device_type=device_type or UNSET,
        )
        data = parse_response(response)
    print_json(data)


@app.command("model")
def show_model() -> None:
    """Show the CNaaS settings JSON-schema model."""
    client = build_client()
    with handle_api_call("show settings model"):
        response = get_settings_model_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("server")
def show_server() -> None:
    """Show the CNaaS server-specific settings."""
    client = build_client()
    with handle_api_call("show server settings"):
        response = get_settings_server_ap_i.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)
