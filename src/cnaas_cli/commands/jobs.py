"""`cnaas jobs ...` — query the CNaaS job queue."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.job import get_job_by_id_api, put_job_by_id_api
from cnaas_nms_api_client.api.jobs import get_jobs_api

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import OutputFormat, print_json, print_success, print_table

app = typer.Typer(help="Inspect and abort CNaaS jobs.", no_args_is_help=True)

JOB_COLUMNS = ["id", "status", "function_name", "start_time", "finish_time", "scheduled_by"]


@app.command("list")
def list_jobs(
    output: OutputFormat = typer.Option(OutputFormat.table, "--output", "-o", help="Output format."),
) -> None:
    """List recent jobs."""
    client = build_client()
    with handle_api_call("list jobs"):
        response = get_jobs_api.sync_detailed(client=client)
        data = parse_response(response)
    if output is OutputFormat.json:
        print_json(data)
    else:
        print_table(data, columns=JOB_COLUMNS, title="CNaaS jobs")


@app.command("show")
def show_job(
    job_id: int = typer.Argument(..., help="Numeric job ID."),
) -> None:
    """Show full details of a single job."""
    client = build_client()
    with handle_api_call(f"show job {job_id}"):
        response = get_job_by_id_api.sync_detailed(job_id, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("abort")
def abort_job(
    job_id: int = typer.Argument(..., help="Numeric job ID to abort."),
) -> None:
    """Abort a running or scheduled job."""
    client = build_client()
    with handle_api_call(f"abort job {job_id}"):
        response = put_job_by_id_api.sync_detailed(job_id, client=client)
        parse_response(response)
    print_success(f"Job {job_id} abort requested.")
