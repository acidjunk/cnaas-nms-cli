"""`cnaas repository ...` — inspect and refresh CNaaS git repositories."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.repository import get_repository_api, put_repository_api
from cnaas_nms_api_client.models.repository import Repository

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json, print_success

app = typer.Typer(help="Inspect and refresh CNaaS-managed git repositories.", no_args_is_help=True)


@app.command("show")
def show_repo(
    repo: str = typer.Argument(..., help="Repository name (e.g. 'settings', 'templates', 'etc')."),
) -> None:
    """Show metadata for a CNaaS-managed git repository."""
    client = build_client()
    with handle_api_call(f"show repository {repo}"):
        response = get_repository_api.sync_detailed(repo, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("refresh")
def refresh_repo(
    repo: str = typer.Argument(..., help="Repository name to refresh."),
    action: str = typer.Option("refresh", help="Action to take (default: 'refresh')."),
) -> None:
    """Refresh (git pull) a CNaaS-managed git repository."""
    body = Repository(action=action)
    client = build_client()
    with handle_api_call(f"refresh repository {repo}"):
        response = put_repository_api.sync_detailed(repo, client=client, body=body)
        data = parse_response(response)
    print_success(f"Repository {repo} refresh triggered.")
    print_json(data)
