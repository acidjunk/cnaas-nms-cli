"""Error handling for CNaaS API calls.

The generated `cnaas-nms-api-client` returns a `Response[Any]` whose `parsed`
attribute is always `None` for the endpoints we use. The actual JSON body lives
in `response.content` (bytes). This module wraps API calls so that:

* HTTP error statuses are converted to friendly Rich-rendered error messages.
* JSON bodies are decoded once and returned to the caller.
* Network errors (httpx exceptions) become a clean exit with code 1.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import httpx
import typer

from .output import print_error, print_warning


class CnaasCliError(Exception):
    """Raised when a CNaaS API call fails or returns an error payload."""

    def __init__(self, message: str, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _extract_messages(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return []
    msg = body.get("message")
    if isinstance(msg, list):
        return [str(m) for m in msg]
    if isinstance(msg, str):
        return [msg]
    return []


def parse_response(response: Any) -> Any:
    """Decode a `Response` object's body to a JSON value (or raise CnaasCliError).

    Accepts both the generated client's `Response[Any]` and a stand-in mock
    that exposes `status_code` and `content`.
    """
    status = int(getattr(response, "status_code", 0))
    raw = getattr(response, "content", b"") or b""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")

    try:
        body = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        body = raw.decode("utf-8", errors="replace")

    if 200 <= status < 300:
        return body

    messages = _extract_messages(body)
    detail = "; ".join(messages) if messages else (str(body) if body else f"HTTP {status}")
    raise CnaasCliError(detail, status_code=status, body=body)


@contextmanager
def handle_api_call(action: str) -> Iterator[None]:
    """Context manager that catches CNaaS/HTTP errors and exits cleanly.

    Args:
        action: Short verb phrase used in error messages, e.g. "list devices".
    """
    try:
        yield
    except CnaasCliError as exc:
        print_error(f"Failed to {action}: {exc}")
        if exc.status_code in (401, 403):
            print_warning(
                "Authentication failed. Check CNAAS_API_KEY or run 'cnaas auth configure'."
            )
        raise typer.Exit(code=1) from exc
    except httpx.HTTPError as exc:
        print_error(f"Network error while trying to {action}: {exc}")
        raise typer.Exit(code=1) from exc
