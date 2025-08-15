import logging
from typing import Any, Dict, List, Optional

from httpx import Client

from ....core.config.model import TmdbConfig
from ..base import BaseApiClient
from ..params import (
    MediaAiringScheduleParams,
    MediaCharactersParams,
    MediaRecommendationParams,
    MediaRelationsParams,
    MediaReviewsParams,
    MediaSearchParams,
    UpdateUserMediaListEntryParams,
    UserMediaListSearchParams,
)
from ..types import (
    AiringScheduleResult,
    CharacterSearchResult,
    MediaItem,
    MediaReview,
    MediaSearchResult,
    Notification,
    UserProfile,
    MediaType,
)
from . import mapper

logger = logging.getLogger(__name__)
TMDB_API_URL = "https://api.themoviedb.org/3"


class TmdbApi(BaseApiClient):
    """TMDB API implementation of the BaseApiClient contract."""

    def __init__(self, config: TmdbConfig, client: Client):
        super().__init__(config, client)
        self.http_client.headers["Accept"] = "application/json"
        if not self.config.api_key:
            raise ValueError("TMDB API key is required.")
        self.api_key = self.config.api_key

    def authenticate(self, token: str) -> Optional[UserProfile]:
        """TMDB uses API keys. This method can be used to validate the key."""
        try:
            params = {"api_key": self.api_key}
            response = self.http_client.get(f"{TMDB_API_URL}/authentication", params=params)
            response.raise_for_status()
            return UserProfile(id="tmdb_user", name="TMDB User", avatar_url="", banner_url="")
        except Exception as e:
            logger.error(f"TMDB authentication check failed: {e}")
            return None

    def is_authenticated(self) -> bool:
        return bool(self.api_key)

    def get_viewer_profile(self) -> Optional[UserProfile]:
        if self.is_authenticated():
            return UserProfile(id="tmdb_user", name="TMDB User", avatar_url="", banner_url="")
        return None

    def search_media(self, params: MediaSearchParams) -> Optional[MediaSearchResult]:
        if not params.query:
            return None

        media_type = "tv" if params.type == MediaType.ANIME else "movie"
        api_params = {
            "api_key": self.api_key,
            "query": params.query,
            "page": params.page or 1,
            "language": self.config.preferred_language,
        }
        try:
            response = self.http_client.get(f"{TMDB_API_URL}/search/{media_type}", params=api_params)
            response.raise_for_status()
            return mapper.to_generic_search_result(response.json(), media_type)
        except Exception as e:
            logger.error(f"Error searching TMDB for '{params.query}': {e}")
            return None

    def search_media_list(
        self, params: UserMediaListSearchParams
    ) -> Optional[MediaSearchResult]:
        logger.warning("Searching user media lists is not yet implemented for TMDB.")
        return None

    def update_list_entry(self, params: UpdateUserMediaListEntryParams) -> bool:
        logger.warning("Updating user media list entries is not yet implemented for TMDB.")
        return False

    def delete_list_entry(self, media_id: int) -> bool:
        logger.warning("Deleting user media list entries is not yet implemented for TMDB.")
        return False

    def get_recommendation_for(
        self, params: MediaRecommendationParams
    ) -> Optional[List[MediaItem]]:
        # This is tricky because we don't know the media type from the ID alone.
        # We will have to try both tv and movie endpoints.
        # For now, we assume 'tv' as this application is anime-focused.
        media_type = "tv"
        api_params = {
            "api_key": self.api_key,
            "page": params.page or 1,
            "language": self.config.preferred_language,
        }
        try:
            response = self.http_client.get(
                f"{TMDB_API_URL}/{media_type}/{params.id}/recommendations", params=api_params
            )
            response.raise_for_status()
            return mapper.to_generic_recommendations(response.json())
        except Exception as e:
            logger.error(f"Error getting recommendations for {params.id}: {e}")
        # We will try both 'tv' and 'movie' endpoints and return the first successful result.
        api_params = {
            "api_key": self.api_key,
            "page": params.page or 1,
            "language": self.config.preferred_language,
        }
        for media_type in ["tv", "movie"]:
            try:
                response = self.http_client.get(
                    f"{TMDB_API_URL}/{media_type}/{params.id}/recommendations", params=api_params
                )
                response.raise_for_status()
                data = response.json()
                # If results are found, return them
                if data.get("results"):
                    return mapper.to_generic_recommendations(data)
            except Exception as e:
                logger.debug(f"Error getting recommendations for {params.id} as {media_type}: {e}")
        logger.error(f"Error getting recommendations for {params.id}: No recommendations found for either 'tv' or 'movie'.")
        return None

    def get_characters_of(
        self, params: MediaCharactersParams
    ) -> Optional[CharacterSearchResult]:
        media_type = "tv"  # Assume tv
        api_params = {"api_key": self.api_key, "language": self.config.preferred_language}
        try:
            response = self.http_client.get(
                f"{TMDB_API_URL}/{media_type}/{params.id}/credits", params=api_params
            )
            response.raise_for_status()
            return mapper.to_generic_characters_result(response.json())
        except Exception as e:
            logger.error(f"Error getting characters for {params.id}: {e}")
            return None

    def get_related_anime_for(
        self, params: MediaRelationsParams
    ) -> Optional[List[MediaItem]]:
        media_type = self._get_tmdb_media_type(params)
        api_params = {
            "api_key": self.api_key,
            "language": self.config.preferred_language,
            "page": 1,
        }
        try:
            response = self.http_client.get(
                f"{TMDB_API_URL}/{media_type}/{params.id}/similar", params=api_params
            )
            response.raise_for_status()
            return mapper.to_generic_relations(response.json())
        except Exception as e:
            logger.error(f"Error getting similar media for {params.id}: {e}")
            return None

    def get_airing_schedule_for(
        self, params: MediaAiringScheduleParams
    ) -> Optional[AiringScheduleResult]:
        logger.warning("Airing schedule is not directly supported by TMDB.")
        return None

    def get_reviews_for(
        self, params: MediaReviewsParams
    ) -> Optional[List[MediaReview]]:
        media_type = DEFAULT_MEDIA_TYPE  # Assume tv
        api_params = {
            "api_key": self.api_key,
            "language": self.config.preferred_language,
            "page": params.page or 1,
        }
        try:
            response = self.http_client.get(
                f"{TMDB_API_URL}/{media_type}/{params.id}/reviews", params=api_params
            )
            response.raise_for_status()
            return mapper.to_generic_reviews_list(response.json())
        except Exception as e:
            logger.error(f"Error getting reviews for {params.id}: {e}")
            return None

    def get_notifications(self) -> Optional[List[Notification]]:
        logger.info("TMDB does not support notifications.")
        return []

    def transform_raw_search_data(self, raw_data: Dict) -> Optional[MediaSearchResult]:
        try:
            # We need to know the media_type, which isn't in the raw data itself.
            # This method might be tricky to use with TMDB.
            # Assuming 'tv' as a default.
            return mapper.to_generic_search_result(raw_data, "tv")
        except Exception as e:
            logger.error(f"Failed to transform raw TMDB search data: {e}")
            return None
