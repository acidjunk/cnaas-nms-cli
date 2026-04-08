# cnaas-nms-cli

A modern, batteries-included terminal client for [**CNaaS-NMS**](https://github.com/SUNET/cnaas-nms)
— the SUNET Campus-Network-as-a-Service controller.

Built on:

- [**Typer**](https://typer.tiangolo.com/) — ergonomic, type-safe sub-commands with auto-generated `--help`
- [**Rich**](https://rich.readthedocs.io/) — colored output, syntax-highlighted JSON, tables
- [**`cnaas-nms-api-client`**](https://pypi.org/project/cnaas-nms-api-client/) — generated HTTP client for the CNaaS-NMS REST API
- [**Pydantic v2**](https://docs.pydantic.dev/) — typed settings & validation
- [**uv**](https://docs.astral.sh/uv/) — fast, reproducible Python environments

`cnaas-nms-cli` lets you list and manage devices, drive ZTP and sync jobs, push
firmware upgrades, inspect linknets/mgmtdomains/groups, refresh git
repositories, query jobs and read settings — all from your shell.

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment variables](#environment-variables)
  - [Persistent config file](#persistent-config-file)
  - [Per-invocation overrides](#per-invocation-overrides)
  - [Precedence](#precedence)
- [Quick start](#quick-start)
- [Output formats](#output-formats)
- [Command reference](#command-reference)
  - [`cnaas devices`](#cnaas-devices)
  - [`cnaas linknets`](#cnaas-linknets)
  - [`cnaas mgmtdomains`](#cnaas-mgmtdomains)
  - [`cnaas groups`](#cnaas-groups)
  - [`cnaas interfaces`](#cnaas-interfaces)
  - [`cnaas firmware`](#cnaas-firmware)
  - [`cnaas jobs`](#cnaas-jobs)
  - [`cnaas repository`](#cnaas-repository)
  - [`cnaas settings`](#cnaas-settings)
  - [`cnaas system`](#cnaas-system)
  - [`cnaas auth`](#cnaas-auth)
- [Shell completion](#shell-completion)
- [Exit codes](#exit-codes)
- [Project layout](#project-layout)
- [Development](#development)
- [Testing](#testing)
- [How it talks to CNaaS](#how-it-talks-to-cnaas)
- [Troubleshooting](#troubleshooting)
- [Releasing](#releasing)
- [License](#license)

---

## Features

- **Hierarchical commands** — 11 command groups with subcommands, each fully documented via `--help`.
- **Rich terminal UI** — colored success/error output, syntax-highlighted JSON, optional table view for `list` commands.
- **Flexible config** — env vars, `.env` files, persistent user config, CLI overrides, or interactive prompt fallback.
- **Friendly errors** — server `message` payloads are surfaced cleanly; 401/403 hint at re-running `cnaas auth configure`; httpx network errors get a clean exit instead of a stack trace.
- **Test-first** — 60 unit tests with `typer.testing.CliRunner` and a fake `Response` stub. No real HTTP calls during testing.
- **Modern Python** — Python 3.10+, Pydantic v2, type-annotated end-to-end.

## Requirements

- Python ≥ 3.10
- A reachable CNaaS-NMS server with API enabled
- A bearer token (JWT) issued by your CNaaS-NMS deployment
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for dependency management

## Installation

```bash
git clone https://github.com/acidjunk/cnaas-nms-cli.git
cd cnaas-nms-cli

uv venv venv                           # create local venv at ./venv/
source venv/bin/activate
uv pip install -e ".[test,dev]"        # install + test/dev extras
```

After installation the `cnaas` script is on your `PATH` (inside the venv):

```bash
cnaas --version
# cnaas-nms-cli 0.1.0
```

> **Note:** This project uses `uv`, never `pip` directly. All install/run/test
> workflows go through `uv venv` / `uv pip` / `uv run`.

## Configuration

### Environment variables

| Variable         | Required | Description                                            |
| ---------------- | -------- | ------------------------------------------------------ |
| `CNAAS_API_KEY`  | yes      | Bearer token used to authenticate against the CNaaS API |
| `CNAAS_BASE_URL` | yes      | Base URL of the CNaaS-NMS API (e.g. `https://cnaas.example.org/api/v1.0`) |

A `.env` file in the current working directory is loaded automatically.

```bash
export CNAAS_BASE_URL="https://cnaas.example.org/api/v1.0"
export CNAAS_API_KEY="eyJhbGciOi..."
```

### Persistent config file

Run `cnaas auth configure` to save credentials so you don't need to export them in every shell:

```bash
cnaas auth configure
# CNaaS base URL: https://cnaas.example.org/api/v1.0
# CNaaS API key: ********
# ✓ Credentials saved to /home/you/.config/cnaas-cli/.cnaas-cli.env
```

The file is written with mode `0600` and respects `$XDG_CONFIG_HOME` (defaults
to `~/.config/cnaas-cli/`). Show the path at any time with:

```bash
cnaas auth config-path
```

### Per-invocation overrides

Two global options override env and config-file values just for one run:

```bash
cnaas --base-url https://staging.example.org/api/v1.0 \
      --api-key   eyJhbGciOi...                       \
      devices list
```

### Precedence

When the CLI resolves a value it walks this list and stops at the first hit:

1. `--api-key` / `--base-url` CLI options
2. `CNAAS_API_KEY` / `CNAAS_BASE_URL` in the process environment
3. `.env` in the current working directory
4. `$XDG_CONFIG_HOME/cnaas-cli/.cnaas-cli.env`
5. **Interactive prompt** (only if stdin **and** stdout are a TTY)
6. **Hard fail with exit 1** otherwise

This makes the CLI safe to use in CI: no value, no implicit prompt, no hang.

### Interactive fallback

If you run `cnaas` in a terminal without env vars or a config file, you'll get
prompted (the API key is masked):

```text
$ cnaas system version
CNaaS base URL: https://cnaas.example.org/api/v1.0
CNaaS API key: ****************
```

## Quick start

```bash
# Smoke-test connectivity
cnaas system version

# Inventory
cnaas devices list                              # Rich table
cnaas devices list -o json                      # raw JSON
cnaas devices show core-sw-01

# ZTP a freshly discovered device
cnaas devices init-check 42 --hostname core-sw-99 --device-type CORE
cnaas devices init       42 --hostname core-sw-99 --device-type CORE

# Sync a single device (dry run first!)
cnaas devices sync --hostname core-sw-01 --dry-run
cnaas devices sync --hostname core-sw-01

# Find your latest sync job
cnaas jobs list -o json
cnaas jobs show 1234

# Refresh templates after a git push
cnaas repository refresh templates
```

## Output formats

`list`-style commands accept `--output / -o`:

| Value   | Notes                                                   |
| ------- | ------------------------------------------------------- |
| `table` | Default. Compact Rich table of common columns.           |
| `json`  | Full server response, syntax-highlighted by Rich.        |

`show`-style commands always print syntax-highlighted JSON.

## Command reference

This is a high-level overview. Run any command with `--help` for the full
option list, including type and default value:

```bash
cnaas devices create --help
```

### `cnaas devices`

| Command                          | Description                                              |
| -------------------------------- | -------------------------------------------------------- |
| `list`                           | List all devices known to CNaaS                          |
| `show <hostname>`                | Show one device                                          |
| `create <hostname> <device_type>`| Create a new device record (many optional fields)        |
| `delete <id> [--factory-default]`| Delete a device by numeric ID                            |
| `init <id> --hostname --device-type` | Trigger ZTP/init                                     |
| `init-check <id> --hostname --device-type` | Pre-flight check before init                   |
| `sync [--hostname/--group/--device-type/--all] [--dry-run] [--force] [--auto-push] [--resync]` | Push (or compute) configuration |
| `generate-config <hostname>`     | Render the candidate config from templates              |
| `running-config <hostname>`      | Pull the live config off the device                     |

### `cnaas linknets`

| Command                                                     | Description              |
| ----------------------------------------------------------- | ------------------------ |
| `list [-o table\|json]`                                     | List all linknets        |
| `show <linknet_id>`                                         | Show one linknet         |
| `create <device_a> <device_b> <port_a> <port_b> [--ipv4-network ...]` | Create a linknet |
| `delete <linknet_id>`                                       | Delete a linknet         |

### `cnaas mgmtdomains`

| Command                                                       | Description |
| ------------------------------------------------------------- | ----------- |
| `list [-o table\|json]`                                       | List all management domains |
| `show <id>`                                                   | Show one mgmtdomain |
| `create <device_a> <device_b> <vlan> <ipv4_gw> <ipv6_gw> [--description ...]` | Create a mgmtdomain |
| `delete <id>`                                                 | Delete a mgmtdomain |

### `cnaas groups`

| Command                | Description                                  |
| ---------------------- | -------------------------------------------- |
| `list`                 | List all device groups                       |
| `show <group_name>`    | List members of a group                      |
| `os-version <group>`   | Show OS-version distribution within a group  |

### `cnaas interfaces`

| Command                       | Description                                   |
| ----------------------------- | --------------------------------------------- |
| `list <hostname>`             | List interfaces on a device                   |
| `status <hostname>`           | Show operational interface status             |
| `set-status <hostname>`       | Bounce-down/bounce-up selected interfaces (templated) |

### `cnaas firmware`

| Command                                            | Description                       |
| -------------------------------------------------- | --------------------------------- |
| `list`                                             | List all firmware images          |
| `show <filename>`                                  | Show one image                    |
| `download --url --sha1 --filename [--no-verify-tls]` | Download to the CNaaS server    |
| `delete <filename>`                                | Delete an image                   |
| `upgrade --url [--hostname / --group] [--filename] [--start-at] [--download] [--activate] [--pre-flight] [--post-flight] [--reboot]` | Trigger an upgrade |

### `cnaas jobs`

| Command          | Description                                |
| ---------------- | ------------------------------------------ |
| `list [-o ...]`  | List recent jobs                           |
| `show <id>`      | Show details of one job                    |
| `abort <id>`     | Abort a running or scheduled job           |

### `cnaas repository`

| Command                  | Description                            |
| ------------------------ | -------------------------------------- |
| `show <repo>`            | Show metadata for a managed git repo   |
| `refresh <repo>`         | `git pull` the repo on the CNaaS server |

Common values for `<repo>`: `settings`, `templates`, `etc`.

### `cnaas settings`

| Command                                            | Description                              |
| -------------------------------------------------- | ---------------------------------------- |
| `show [--hostname ...] [--device-type ...]`        | Show effective settings (optionally filtered) |
| `model`                                            | Show the JSON-schema settings model      |
| `server`                                           | Show server-side settings                |

### `cnaas system`

| Command            | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `version`          | Show CNaaS server version                                |
| `shutdown [--yes]` | Gracefully shut the CNaaS API server down (admin only)  |

### `cnaas auth`

| Command         | Description                                                       |
| --------------- | ----------------------------------------------------------------- |
| `whoami`        | Show the identity associated with the current API key             |
| `permissions`   | Show the permissions granted by the current API key               |
| `refresh`       | Refresh the current JWT (returns a new token)                     |
| `configure`     | Persist `CNAAS_BASE_URL` + `CNAAS_API_KEY` to the user config file |
| `config-path`   | Print the absolute path of the persistent config file              |

## Shell completion

Typer ships completion for bash, zsh, fish and PowerShell out of the box:

```bash
cnaas --install-completion
# Or just print the script and add it manually:
cnaas --show-completion
```

## Exit codes

| Code | Meaning                                                                    |
| ---- | -------------------------------------------------------------------------- |
| `0`  | Success                                                                    |
| `1`  | API error (4xx/5xx), network error, missing config in non-interactive mode |
| `2`  | Typer/CLI usage error (wrong flags, missing required argument)             |

## Project layout

```
cnaas-nms-cli/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/cnaas_cli/
│   ├── __init__.py             # __version__
│   ├── __main__.py             # python -m cnaas_cli
│   ├── main.py                 # root Typer app + global options
│   ├── config.py               # Pydantic settings + interactive prompt + persistent file
│   ├── client.py               # AuthenticatedClient factory (lru_cache)
│   ├── errors.py               # parse_response + handle_api_call context manager
│   ├── output.py               # Rich console, print_json, print_table, OutputFormat
│   └── commands/
│       ├── devices.py
│       ├── linknets.py
│       ├── mgmtdomains.py
│       ├── groups.py
│       ├── interfaces.py
│       ├── firmware.py
│       ├── jobs.py
│       ├── repository.py
│       ├── settings.py
│       ├── system.py
│       └── auth.py
└── tests/
    ├── conftest.py             # CliRunner fixture, FakeResponse, fake_client, env isolation
    ├── test_main.py
    ├── test_config.py
    ├── test_errors.py
    ├── test_devices.py
    ├── test_linknets.py
    ├── test_mgmtdomains.py
    ├── test_groups.py
    ├── test_interfaces.py
    ├── test_firmware.py
    ├── test_jobs.py
    ├── test_repository.py
    ├── test_settings.py
    ├── test_system.py
    └── test_auth.py
```

## Development

```bash
uv venv venv
source venv/bin/activate
uv pip install -e ".[test,dev]"

uv run cnaas --help               # try the CLI
uv run pytest                     # run tests
uv run ruff check src tests       # lint
uv run ruff check --fix src tests # auto-fix lint
```

`venv/` is gitignored.

### Adding a new command

1. Find the matching endpoint module under
   `cnaas_nms_api_client/api/<resource>/<action>_api.py`. The generated client
   exposes a `sync_detailed(...)` function for each one.
2. Add a new `@app.command(...)` to the relevant `src/cnaas_cli/commands/<group>.py`,
   following the existing pattern:

   ```python
   @app.command("foo")
   def foo(arg: str = typer.Argument(..., help="...")) -> None:
       """Short description shown in --help."""
       client = build_client()
       with handle_api_call("do foo"):
           response = some_endpoint_module.sync_detailed(arg, client=client)
           data = parse_response(response)
       print_json(data)
   ```

3. Add a test in `tests/test_<group>.py` using `stub_endpoint(...)` from
   `conftest.py`. No real HTTP calls.

## Testing

```bash
uv run pytest -q              # quick run
uv run pytest -v              # verbose
uv run pytest tests/test_devices.py::test_create_device
uv run pytest --cov=cnaas_cli --cov-report=term-missing
```

The test suite is hermetic: an autouse fixture sets fake env vars, clears the
cached AuthenticatedClient, and isolates the persistent config file under a
`tmp_path` `XDG_CONFIG_HOME`. Each test stubs the specific
`sync_detailed` function it expects to be called and asserts on its arguments.

There are **60 tests** at the moment, covering every command plus error paths
(401 → exit 1 + auth hint, missing config in non-TTY → exit 1, validation
errors on `sync` / `firmware upgrade`).

## How it talks to CNaaS

`cnaas-nms-api-client` is an OpenAPI-generated client. Each REST endpoint lives
in its own file and exposes:

```python
def sync_detailed(*, client: AuthenticatedClient, ...) -> Response[Any]: ...
```

Two important quirks of the generated client influenced this CLI's design:

1. **`response.parsed` is always `None`** for the endpoints we use — the actual
   JSON body sits in `response.content` (bytes). `cnaas_cli.errors.parse_response`
   decodes it and either returns the parsed value or raises `CnaasCliError`
   carrying the server's `message` field for clean rendering.
2. **POST/PUT/DELETE bodies are typed `attrs` models**, not free dicts. The CLI
   constructs them from your CLI flags via `Model(**{k: v for k, v in opts.items() if v is not None})`.

Authentication uses a Bearer JWT in the `Authorization` header — see
`cnaas_nms_api_client.AuthenticatedClient`.

## Troubleshooting

| Symptom                                                 | Likely cause / fix                                                  |
| ------------------------------------------------------- | ------------------------------------------------------------------- |
| `✗ Failed to ...: HTTP 401` and `Authentication failed.` hint | Token is expired or wrong. Re-run `cnaas auth configure`.    |
| `✗ Missing CNAAS_BASE_URL ...` in CI                    | No env var, no `.env`, no TTY → set the env var explicitly in CI.    |
| `Network error while trying to ...`                     | The CNaaS server is unreachable / TLS error / DNS. Check `--base-url`. |
| Output is wrapped/garbled in a small terminal           | Force JSON: `cnaas devices list -o json`                            |
| `command not found: cnaas`                              | The venv isn't on PATH. `source venv/bin/activate` or use `uv run cnaas …`. |
| Pre-existing token in the config file is being used     | Override with `--api-key` or `unset CNAAS_API_KEY` is not enough — the config file wins over an unset env. Edit/remove `~/.config/cnaas-cli/.cnaas-cli.env`. |

## Releasing

Releases are published to [PyPI](https://pypi.org/p/cnaas-nms-cli) automatically
by `.github/workflows/publish.yml` using **PyPI Trusted Publishing** (OIDC) — no
API tokens are stored in the repo.

One-time setup on PyPI:

1. Create the project `cnaas-nms-cli` on PyPI (or use an existing one).
2. Under the project's *Publishing* settings, add a new **trusted publisher**:
   - Owner: `acidjunk`
   - Repository: `cnaas-nms-cli`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. In the GitHub repository settings, create an environment named `pypi`
   (Settings → Environments → New environment).

To cut a release:

```bash
# 1. Bump the version in pyproject.toml
$EDITOR pyproject.toml          # e.g. version = "0.2.0"

# 2. Commit and tag
git commit -am "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

Pushing the `v*.*.*` tag triggers `publish.yml`, which:

1. Verifies the tag matches `pyproject.toml`'s `version`.
2. Runs lint + tests.
3. Builds sdist + wheel via `uv build`.
4. Uploads them to PyPI via Trusted Publishing.
5. Attaches the built distributions to a GitHub release with auto-generated notes.

You can also trigger the workflow manually from the Actions tab
(`workflow_dispatch`) — useful for re-running after a PyPI hiccup. Manual runs
skip the GitHub-release step (which is gated on the tag).

## License

Apache-2.0 — see `pyproject.toml`. Same license as the upstream
`cnaas-nms-api-client` and `cnaas-nms` projects.
