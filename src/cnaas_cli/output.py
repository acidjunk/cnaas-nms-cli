"""Rich-based output helpers shared across all commands."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from enum import Enum
from typing import Any

from rich.console import Console
from rich.json import JSON
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    """Supported output formats for list/show commands."""

    table = "table"
    json = "json"


def print_success(msg: str) -> None:
    console.print(f"[bold green]✓[/bold green] {msg}")


def print_warning(msg: str) -> None:
    err_console.print(f"[bold yellow]![/bold yellow] {msg}")


def print_error(msg: str) -> None:
    err_console.print(f"[bold red]✗[/bold red] {msg}")


def print_json(data: Any) -> None:
    """Pretty-print a JSON-serialisable value with syntax highlighting."""
    if isinstance(data, (str, bytes)):
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        try:
            console.print(JSON(text))
            return
        except Exception:
            console.print(text)
            return
    console.print(JSON(json.dumps(data, default=str)))


def _extract_rows(data: Any) -> list[dict[str, Any]]:
    """Best-effort extraction of a list of dict rows from a CNaaS API payload."""
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        # CNaaS responses are wrapped: {"status": "success", "data": {"<key>": [...]}}
        payload = data.get("data", data)
        if isinstance(payload, list):
            return [r for r in payload if isinstance(r, dict)]
        if isinstance(payload, dict):
            for value in payload.values():
                if isinstance(value, list):
                    return [r for r in value if isinstance(r, dict)]
            return [payload]
    return []


def print_table(
    data: Any,
    columns: Sequence[str] | None = None,
    title: str | None = None,
) -> None:
    """Render a list of dicts as a Rich table; falls back to JSON if no rows.

    Args:
        data: Either a list of dicts or a CNaaS-style wrapped response.
        columns: Subset of keys to render. Defaults to keys of the first row.
        title: Optional table title.
    """
    rows = _extract_rows(data)
    if not rows:
        print_json(data)
        return

    cols: Iterable[str] = columns or list(rows[0].keys())
    table = Table(title=title, show_lines=False, header_style="bold cyan")
    for col in cols:
        table.add_column(col)
    for row in rows:
        table.add_row(*[_stringify(row.get(c)) for c in cols])
    console.print(table)


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str)
    return str(value)
