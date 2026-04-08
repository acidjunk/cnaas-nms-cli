"""`cnaas mgmtdomains ...` — manage CNaaS management domains."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.mgmtdomain import (
    delete_mgmtdomain_by_id_api,
    get_mgmtdomain_by_id_api,
)
from cnaas_nms_api_client.api.mgmtdomains import (
    get_mgmtdomains_api,
    post_mgmtdomains_api,
)
from cnaas_nms_api_client.models.mgmtdomain import Mgmtdomain

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import OutputFormat, print_json, print_success, print_table

app = typer.Typer(help="Manage CNaaS management domains.", no_args_is_help=True)

COLUMNS = ["id", "device_a", "device_b", "vlan", "ipv4_gw", "ipv6_gw", "description"]


@app.command("list")
def list_mgmtdomains(
    output: OutputFormat = typer.Option(OutputFormat.table, "--output", "-o", help="Output format."),
) -> None:
    """List all management domains."""
    client = build_client()
    with handle_api_call("list mgmtdomains"):
        response = get_mgmtdomains_api.sync_detailed(client=client)
        data = parse_response(response)
    if output is OutputFormat.json:
        print_json(data)
    else:
        print_table(data, columns=COLUMNS, title="CNaaS mgmtdomains")


@app.command("show")
def show_mgmtdomain(
    mgmtdomain_id: int = typer.Argument(..., help="Numeric mgmtdomain ID."),
) -> None:
    """Show details of a single management domain."""
    client = build_client()
    with handle_api_call(f"show mgmtdomain {mgmtdomain_id}"):
        response = get_mgmtdomain_by_id_api.sync_detailed(mgmtdomain_id, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("create")
def create_mgmtdomain(
    device_a: str = typer.Argument(..., help="Hostname of device A."),
    device_b: str = typer.Argument(..., help="Hostname of device B."),
    vlan: int = typer.Argument(..., help="VLAN ID for the management network."),
    ipv4_gw: str = typer.Argument(..., help="IPv4 gateway address (CIDR)."),
    ipv6_gw: str = typer.Argument(..., help="IPv6 gateway address (CIDR)."),
    description: str | None = typer.Option(None, help="Optional description of the mgmtdomain."),
) -> None:
    """Create a new management domain."""
    body = Mgmtdomain(
        device_a=device_a,
        device_b=device_b,
        vlan=vlan,
        ipv4_gw=ipv4_gw,
        ipv6_gw=ipv6_gw,
        **({"description": description} if description else {}),
    )
    client = build_client()
    with handle_api_call("create mgmtdomain"):
        response = post_mgmtdomains_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success("Mgmtdomain created.")
    print_json(data)


@app.command("delete")
def delete_mgmtdomain(
    mgmtdomain_id: int = typer.Argument(..., help="Numeric mgmtdomain ID to delete."),
) -> None:
    """Delete a management domain by ID."""
    client = build_client()
    with handle_api_call(f"delete mgmtdomain {mgmtdomain_id}"):
        response = delete_mgmtdomain_by_id_api.sync_detailed(mgmtdomain_id, client=client)
        parse_response(response)
    print_success(f"Mgmtdomain {mgmtdomain_id} deleted.")
