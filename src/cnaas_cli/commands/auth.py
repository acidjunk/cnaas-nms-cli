"""`cnaas auth ...` — auth + local credential management."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.auth import get_identity_api, get_permissions_api, post_refresh_api

from ..client import build_client
from ..config import config_file_path, save_settings
from ..errors import handle_api_call, parse_response
from ..output import console, print_json, print_success

app = typer.Typer(help="Authenticate against CNaaS and manage local credentials.", no_args_is_help=True)


@app.command("whoami")
def whoami() -> None:
    """Show the identity associated with the current CNaaS API key."""
    client = build_client()
    with handle_api_call("get identity"):
        response = get_identity_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("permissions")
def permissions() -> None:
    """Show the permissions granted by the current CNaaS API key."""
    client = build_client()
    with handle_api_call("get permissions"):
        response = get_permissions_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("refresh")
def refresh() -> None:
    """Refresh the current CNaaS JWT (returns a new token)."""
    client = build_client()
    with handle_api_call("refresh token"):
        response = post_refresh_api.sync_detailed(client=client)
        data = parse_response(response)
    print_success("Token refreshed.")
    print_json(data)


@app.command("configure")
def configure(
    base_url: str = typer.Option(..., prompt="CNaaS base URL", help="Base URL of the CNaaS API (.../api/v1.0)."),
    api_key: str = typer.Option(
        ...,
        prompt="CNaaS API key",
        hide_input=True,
        confirmation_prompt=False,
        help="Bearer token for the CNaaS API.",
    ),
) -> None:
    """Persist CNaaS credentials to the user config file (mode 0600)."""
    path = save_settings(api_key=api_key, base_url=base_url)
    print_success(f"Credentials saved to {path}")
    console.print(
        "[dim]These will be loaded automatically on subsequent runs. "
        "Override at any time with --api-key / --base-url or by setting CNAAS_API_KEY / CNAAS_BASE_URL.[/dim]"
    )


@app.command("config-path")
def show_config_path() -> None:
    """Print the path of the persistent CNaaS CLI config file."""
    console.print(str(config_file_path()))
