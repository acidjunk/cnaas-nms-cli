"""`cnaas devices ...` — manage CNaaS devices."""

from __future__ import annotations

import typer
from cnaas_nms_api_client.api.device import (
    delete_device_by_id_api,
    get_device_by_hostname_api,
    get_device_generate_config_api,
    get_device_running_config_api,
    post_device_api,
)
from cnaas_nms_api_client.api.device_init import post_device_init_api
from cnaas_nms_api_client.api.device_initcheck import post_device_init_check_api
from cnaas_nms_api_client.api.device_syncto import post_device_sync_api
from cnaas_nms_api_client.api.devices import get_devices_api
from cnaas_nms_api_client.models.delete_devcie import DeleteDevcie
from cnaas_nms_api_client.models.device import Device
from cnaas_nms_api_client.models.device_init import DeviceInit
from cnaas_nms_api_client.models.device_initcheck import DeviceInitcheck
from cnaas_nms_api_client.models.device_sync import DeviceSync

from ..client import build_client
from ..errors import handle_api_call, parse_response
from ..output import OutputFormat, print_json, print_success, print_table

app = typer.Typer(help="Manage CNaaS devices (list, show, create, sync, init, ...).", no_args_is_help=True)

DEVICE_COLUMNS = ["id", "hostname", "device_type", "platform", "state", "management_ip", "synchronized"]


@app.command("list")
def list_devices(
    output: OutputFormat = typer.Option(
        OutputFormat.table, "--output", "-o", help="Output format: 'table' or 'json'."
    ),
) -> None:
    """List all devices known to CNaaS."""
    client = build_client()
    with handle_api_call("list devices"):
        response = get_devices_api.sync_detailed(client=client)
        data = parse_response(response)
    if output is OutputFormat.json:
        print_json(data)
    else:
        print_table(data, columns=DEVICE_COLUMNS, title="CNaaS devices")


@app.command("show")
def show_device(
    hostname: str = typer.Argument(..., help="Hostname of the device to look up."),
) -> None:
    """Show detailed information about a single device."""
    client = build_client()
    with handle_api_call(f"show device {hostname}"):
        response = get_device_by_hostname_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("create")
def create_device(
    hostname: str = typer.Argument(..., help="Hostname of the new device."),
    device_type: str = typer.Argument(..., help="Device type (e.g. CORE, DIST, ACCESS)."),
    platform: str = typer.Option("junos", help="NAPALM/Nornir platform name (junos, eos, ios, iosxr, nxos)."),
    state: str = typer.Option("MANAGED", help="Initial device state (e.g. MANAGED, UNMANAGED, INIT)."),
    description: str | None = typer.Option(None, help="Free-text description of the device."),
    site_id: int | None = typer.Option(None, help="Numeric site ID this device belongs to."),
    management_ip: str | None = typer.Option(None, help="Management IP address."),
    infra_ip: str | None = typer.Option(None, help="Infrastructure (loopback) IP address."),
    dhcp_ip: str | None = typer.Option(None, help="DHCP-assigned address used during ZTP."),
    serial: str | None = typer.Option(None, help="Hardware serial number."),
    ztp_mac: str | None = typer.Option(None, help="MAC address used for zero-touch provisioning."),
    vendor: str | None = typer.Option(None, help="Hardware vendor (e.g. Juniper, Arista)."),
    model: str | None = typer.Option(None, help="Hardware model identifier."),
    os_version: str | None = typer.Option(None, help="Operating system version string."),
    synchronized: bool | None = typer.Option(None, help="Mark device as synchronized."),
    port: int | None = typer.Option(None, help="Management port (when not 22/830)."),
) -> None:
    """Create a new device record in CNaaS."""
    optional: dict[str, object] = {
        "site_id": site_id,
        "description": description,
        "management_ip": management_ip,
        "infra_ip": infra_ip,
        "dhcp_ip": dhcp_ip,
        "serial": serial,
        "ztp_mac": ztp_mac,
        "vendor": vendor,
        "model": model,
        "os_version": os_version,
        "synchronized": synchronized,
        "port": port,
    }
    body = Device(
        hostname=hostname,
        platform=platform,
        state=state,
        device_type=device_type,
        **{k: v for k, v in optional.items() if v is not None},
    )
    client = build_client()
    with handle_api_call(f"create device {hostname}"):
        response = post_device_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success(f"Device {hostname} created.")
    print_json(data)


@app.command("delete")
def delete_device(
    device_id: int = typer.Argument(..., help="Numeric device ID to delete."),
    factory_default: bool = typer.Option(
        False, "--factory-default", help="Reset the device to factory defaults on delete."
    ),
) -> None:
    """Delete a device by its numeric ID."""
    body = DeleteDevcie(factory_default=factory_default) if factory_default else DeleteDevcie()
    client = build_client()
    with handle_api_call(f"delete device {device_id}"):
        response = delete_device_by_id_api.sync_detailed(device_id, client=client, body=body)
        parse_response(response)
    print_success(f"Device {device_id} deleted.")


@app.command("init")
def init_device(
    device_id: int = typer.Argument(..., help="Numeric device ID to initialize."),
    hostname: str = typer.Option(..., help="Target hostname to assign during init."),
    device_type: str = typer.Option(..., help="Device type (CORE, DIST, ACCESS)."),
) -> None:
    """Trigger initial provisioning (ZTP) of a discovered device."""
    body = DeviceInit(hostname=hostname, device_type=device_type)
    client = build_client()
    with handle_api_call(f"init device {device_id}"):
        response = post_device_init_api.sync_detailed(device_id, client=client, body=body)
        data = parse_response(response)
    print_success(f"Init triggered for device {device_id}.")
    print_json(data)


@app.command("init-check")
def init_check(
    device_id: int = typer.Argument(..., help="Numeric device ID to validate."),
    hostname: str = typer.Option(..., help="Hostname intended for this device."),
    device_type: str = typer.Option(..., help="Device type (CORE, DIST, ACCESS)."),
    mlag_peer_id: int | None = typer.Option(None, help="MLAG peer device ID, if applicable."),
    mlag_peer_hostname: str | None = typer.Option(None, help="MLAG peer hostname, if applicable."),
) -> None:
    """Run pre-flight checks against a device before init."""
    optional: dict[str, object] = {
        "mlag_peer_id": mlag_peer_id,
        "mlag_peer_hostname": mlag_peer_hostname,
    }
    body = DeviceInitcheck(
        hostname=hostname,
        device_type=device_type,
        **{k: v for k, v in optional.items() if v is not None},
    )
    client = build_client()
    with handle_api_call(f"init-check device {device_id}"):
        response = post_device_init_check_api.sync_detailed(device_id, client=client, body=body)
        data = parse_response(response)
    print_json(data)


@app.command("sync")
def sync_devices(
    hostname: str | None = typer.Option(None, help="Sync a single device by hostname."),
    group: str | None = typer.Option(None, help="Sync all devices in a group."),
    device_type: str | None = typer.Option(None, help="Sync all devices of a given type."),
    all_devices: bool = typer.Option(False, "--all", help="Sync all devices."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't push changes; only compute the diff."),
    force: bool = typer.Option(False, "--force", help="Force sync even if device looks in-sync."),
    auto_push: bool = typer.Option(False, "--auto-push", help="Automatically push the diff after dry-run."),
    resync: bool = typer.Option(False, "--resync", help="Treat current config as untrusted and re-sync."),
) -> None:
    """Start a configuration sync to one or more devices."""
    if not any([hostname, group, device_type, all_devices]):
        raise typer.BadParameter("Specify at least one of --hostname, --group, --device-type, or --all.")

    optional: dict[str, object] = {
        "hostname": hostname,
        "group": group,
        "device_type": device_type,
        "all_": all_devices or None,
        "dry_run": dry_run or None,
        "force": force or None,
        "auto_push": auto_push or None,
        "resync": resync or None,
    }
    body = DeviceSync(**{k: v for k, v in optional.items() if v is not None})
    client = build_client()
    with handle_api_call("start device sync"):
        response = post_device_sync_api.sync_detailed(client=client, body=body)
        data = parse_response(response)
    print_success("Sync job submitted.")
    print_json(data)


@app.command("generate-config")
def generate_config(
    hostname: str = typer.Argument(..., help="Hostname of the device to render the config for."),
) -> None:
    """Render the candidate (templated) configuration for a device."""
    client = build_client()
    with handle_api_call(f"generate config for {hostname}"):
        response = get_device_generate_config_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_json(data)


@app.command("running-config")
def running_config(
    hostname: str = typer.Argument(..., help="Hostname of the device whose live config to fetch."),
) -> None:
    """Fetch the currently running config from a device."""
    client = build_client()
    with handle_api_call(f"fetch running config for {hostname}"):
        response = get_device_running_config_api.sync_detailed(hostname, client=client)
        data = parse_response(response)
    print_json(data)
