from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from httpx import Client

from ...core.utils.networking import random_user_agent

if TYPE_CHECKING:
    from ...core.config import AppConfig
    from .base import BaseApiClient

logger = logging.getLogger(__name__)

# Map the client name to its import path AND the config section it needs.
API_CLIENTS = {
    "anilist": ("fastanime.libs.media_api.anilist.api.AniListApi", "anilist"),
    "jikan": ("fastanime.libs.media_api.jikan.api.JikanApi", "jikan"),  # For the future
    "tmdb": ("fastanime.libs.media_api.tmdb.api.TmdbApi", "tmdb"),
}


def create_api_client(client_name: str, config: AppConfig) -> BaseApiClient:
    """
    Factory to create an instance of a specific API client, injecting only
    the relevant section of the application configuration.
    """
    if client_name not in API_CLIENTS:
        raise ValueError(f"Unsupported API client: '{client_name}'")

    import_path, config_section_name = API_CLIENTS[client_name]
    module_name, class_name = import_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_name)
        client_class = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load API client '{client_name}': {e}") from e

    # Create a shared httpx client for the API
    http_client = Client(headers={"User-Agent": random_user_agent()})

    # Retrieve the specific config section from the main AppConfig
    scoped_config = getattr(config, config_section_name)

    # Inject the scoped config into the client's constructor
    return client_class(scoped_config, http_client)
