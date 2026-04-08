"""`cnaas groups ...` — inspect CNaaS device groups."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.groups import (
    get_groups_api,
    get_groups_api_by_name,
    get_groups_api_by_name_osversion,
)

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json

app = typer.Typer(help="Inspect CNaaS device groups.", no_args_is_help=True)


@app.command("list")
def list_groups() -> None:
    """List all device groups."""
    client = build_client()
    with handle_api_call("list groups"):
        response = get_groups_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("show")
def show_group(
    group_name: str = typer.Argument(..., help="Group name to look up."),
) -> None:
    """Show members of a device group."""
    client = build_client()
    with handle_api_call(f"show group {group_name}"):
        response = get_groups_api_by_name.sync_detailed(group_name, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("os-version")
def os_version(
    group_name: str = typer.Argument(..., help="Group name."),
) -> None:
    """Show the OS version distribution within a device group."""
    client = build_client()
    with handle_api_call(f"get OS versions for group {group_name}"):
        response = get_groups_api_by_name_osversion.sync_detailed(group_name, client=client)
        data = parse_response(response)
    print_json(data)
