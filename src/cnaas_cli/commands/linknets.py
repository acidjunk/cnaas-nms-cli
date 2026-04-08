"""`cnaas linknets ...` — manage CNaaS inter-device links."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.linknet import (
    delete_linknet_by_id_api,
    get_linknet_by_id_api,
)
from cnaas_nms_api_client.api.linknets import (
    get_linknets_api,
    post_linknets_api,
)
from cnaas_nms_api_client.models.linknets import Linknets

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import OutputFormat, print_json, print_success, print_table

app = typer.Typer(help="Manage CNaaS linknets.", no_args_is_help=True)

LINKNET_COLUMNS = ["id", "device_a", "device_a_port", "device_b", "device_b_port", "ipv4_network"]


@app.command("list")
def list_linknets(
    output: OutputFormat = typer.Option(OutputFormat.table, "--output", "-o", help="Output format."),
) -> None:
    """List all linknets."""
    client = build_client()
    with handle_api_call("list linknets"):
        response = get_linknets_api.sync_detailed(client=client)
        data = parse_response(response)
    if output is OutputFormat.json:
        print_json(data)
    else:
        print_table(data, columns=LINKNET_COLUMNS, title="CNaaS linknets")


@app.command("show")
def show_linknet(
    linknet_id: int = typer.Argument(..., help="Numeric linknet ID."),
) -> None:
    """Show details of a single linknet."""
    client = build_client()
    with handle_api_call(f"show linknet {linknet_id}"):
        response = get_linknet_by_id_api.sync_detailed(linknet_id, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("create")
def create_linknet(
    device_a: str = typer.Argument(..., help="Hostname of device A."),
    device_b: str = typer.Argument(..., help="Hostname of device B."),
    device_a_port: str = typer.Argument(..., help="Interface name on device A."),
    device_b_port: str = typer.Argument(..., help="Interface name on device B."),
    ipv4_network: str | None = typer.Option(None, help="Optional IPv4 network in CIDR notation (e.g. 10.0.0.0/30)."),
) -> None:
    """Create a new linknet between two devices."""
    optional: dict[str, object] = {"ipv4_network": ipv4_network}
    body = Linknets(
        device_a=device_a,
        device_b=device_b,
        device_a_port=device_a_port,
        device_b_port=device_b_port,
        **{k: v for k, v in optional.items() if v is not None},
    )
    client = build_client()
    with handle_api_call(f"create linknet {device_a}<->{device_b}"):
        response = post_linknets_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success(f"Linknet {device_a}<->{device_b} created.")
    print_json(data)


@app.command("delete")
def delete_linknet(
    linknet_id: int = typer.Argument(..., help="Numeric linknet ID to delete."),
) -> None:
    """Delete a linknet by its numeric ID."""
    client = build_client()
    with handle_api_call(f"delete linknet {linknet_id}"):
        response = delete_linknet_by_id_api.sync_detailed(linknet_id, client=client)
        parse_response(response)
    print_success(f"Linknet {linknet_id} deleted.")
