"""`cnaas interfaces ...` — manage device interfaces."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.device import (
    get_interface_api,
    get_interface_status_api,
    put_interface_status_api,
)

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json, print_success

app = typer.Typer(help="Manage device interfaces.", no_args_is_help=True)


@app.command("list")
def list_interfaces(
    hostname: str = typer.Argument(..., help="Hostname of the device."),
) -> None:
    """List interfaces on a device."""
    client = build_client()
    with handle_api_call(f"list interfaces on {hostname}"):
        response = get_interface_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("status")
def interface_status(
    hostname: str = typer.Argument(..., help="Hostname of the device."),
) -> None:
    """Show the operational status of a device's interfaces."""
    client = build_client()
    with handle_api_call(f"get interface status for {hostname}"):
        response = get_interface_status_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("set-status")
def set_status(
    hostname: str = typer.Argument(..., help="Hostname of the device."),
) -> None:
    """Update the administrative status of one or more interfaces (server-side body)."""
    client = build_client()
    with handle_api_call(f"set interface status on {hostname}"):
        response = put_interface_status_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_success("Interface status updated.")
    print_json(data)
