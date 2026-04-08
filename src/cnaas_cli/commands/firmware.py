"""`cnaas firmware ...` — manage firmware images and upgrades."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.firmware import (
    delete_firmware_image_api,
    get_firmware_api,
    get_firmware_image_api,
    post_firmware_api,
    post_firmware_upgrade_api,
)
from cnaas_nms_api_client.models.firmware_download import FirmwareDownload
from cnaas_nms_api_client.models.firmware_upgrade import FirmwareUpgrade

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import print_json, print_success

app = typer.Typer(help="Manage CNaaS firmware images and upgrades.", no_args_is_help=True)


@app.command("list")
def list_firmware() -> None:
    """List all firmware images stored on the CNaaS server."""
    client = build_client()
    with handle_api_call("list firmware"):
        response = get_firmware_api.sync_detailed(client=client)
        data = parse_response(response)
    print_json(data)


@app.command("show")
def show_firmware(
    filename: str = typer.Argument(..., help="Firmware image filename."),
) -> None:
    """Show details of a single firmware image."""
    client = build_client()
    with handle_api_call(f"show firmware {filename}"):
        response = get_firmware_image_api.sync_detailed(filename, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("download")
def download_firmware(
    url: str = typer.Option(..., help="HTTP(S) URL to download the image from."),
    sha1: str = typer.Option(..., help="Expected SHA1 checksum of the file."),
    filename: str = typer.Option(..., help="Filename to store the firmware image as."),
    verify_tls: bool = typer.Option(True, "--verify-tls/--no-verify-tls", help="Verify TLS when downloading."),
) -> None:
    """Download a firmware image to the CNaaS server."""
    body = FirmwareDownload(url=url, sha1=sha1, filename=filename, verify_tls=verify_tls)
    client = build_client()
    with handle_api_call(f"download firmware {filename}"):
        response = post_firmware_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success(f"Firmware download for {filename} started.")
    print_json(data)


@app.command("delete")
def delete_firmware(
    filename: str = typer.Argument(..., help="Firmware image filename to delete."),
) -> None:
    """Delete a firmware image from the CNaaS server."""
    client = build_client()
    with handle_api_call(f"delete firmware {filename}"):
        response = delete_firmware_image_api.sync_detailed(filename, client=client)
        parse_response(response)
    print_success(f"Firmware {filename} deleted.")


@app.command("upgrade")
def upgrade_firmware(
    url: str = typer.Option(..., help="HTTP(S) URL of the firmware image."),
    hostname: str | None = typer.Option(None, help="Upgrade a single device by hostname."),
    group: str | None = typer.Option(None, help="Upgrade all devices in a group."),
    filename: str | None = typer.Option(None, help="Filename of the image on the CNaaS server."),
    start_at: str | None = typer.Option(None, help="ISO timestamp at which to start the upgrade."),
    download: bool = typer.Option(False, "--download", help="Trigger pre-download of the image."),
    activate: bool = typer.Option(False, "--activate", help="Activate the new image."),
    pre_flight: bool = typer.Option(False, "--pre-flight", help="Run pre-flight checks."),
    post_flight: bool = typer.Option(False, "--post-flight", help="Run post-flight checks."),
    post_wattime: int | None = typer.Option(None, help="Wait time (seconds) after upgrade."),
    reboot: bool = typer.Option(False, "--reboot", help="Reboot the device after upgrade."),
) -> None:
    """Trigger a firmware upgrade on one or more devices."""
    if not (hostname or group):
        raise typer.BadParameter("Specify --hostname or --group.")

    optional: dict[str, object] = {
        "hostname": hostname,
        "group": group,
        "filename": filename,
        "start_at": start_at,
        "download": download or None,
        "activate": activate or None,
        "pre_flight": pre_flight or None,
        "post_flight": post_flight or None,
        "post_wattime": post_wattime,
        "reboot": reboot or None,
    }
    body = FirmwareUpgrade(url=url, **{k: v for k, v in optional.items() if v is not None})
    client = build_client()
    with handle_api_call("trigger firmware upgrade"):
        response = post_firmware_upgrade_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success("Firmware upgrade job submitted.")
    print_json(data)
