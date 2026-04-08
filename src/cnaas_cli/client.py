"""Factory for the underlying ``cnaas-nms-api-client`` AuthenticatedClient."""

from __future__ import annotations

from functools import lru_cache

from cnaas_nms_api_client import AuthenticatedClient

from .config import Settings, get_settings


@lru_cache(maxsize=4)
def _cached_client(base_url: str, token: str) -> AuthenticatedClient:
    return AuthenticatedClient(base_url=base_url, token=token)


def build_client(settings: Settings | None = None) -> AuthenticatedClient:
    """Return a (cached) AuthenticatedClient for the resolved settings."""
    settings = settings or get_settings()
    return _cached_client(settings.base_url, settings.api_key.get_secret_value())
