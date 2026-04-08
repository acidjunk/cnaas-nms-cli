"""Tests for cnaas_cli.errors."""

from __future__ import annotations

import pytest

from cnaas_cli.errors import CnaasCliError, parse_response

from .conftest import FakeResponse


def test_parse_response_ok():
    payload = {"status": "success", "data": {"devices": []}}
    assert parse_response(FakeResponse.ok(payload)) == payload


def test_parse_response_error_string():
    with pytest.raises(CnaasCliError) as exc_info:
        parse_response(FakeResponse.error(404, "Device not found"))
    assert exc_info.value.status_code == 404
    assert "Device not found" in str(exc_info.value)


def test_parse_response_error_list():
    with pytest.raises(CnaasCliError) as exc_info:
        parse_response(FakeResponse.error(400, ["bad hostname", "missing field"]))
    assert "bad hostname" in str(exc_info.value)
    assert "missing field" in str(exc_info.value)


def test_parse_response_empty_body():
    assert parse_response(FakeResponse(status_code=204, content=b"")) is None
