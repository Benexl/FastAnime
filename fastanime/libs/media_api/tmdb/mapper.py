import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..types import (
    Character,
    CharacterImage,
    CharacterName,
    CharacterSearchResult,
    MediaImage,
    MediaItem,
    MediaReview,
    MediaSearchResult,
    MediaTitle,
    PageInfo,
    Reviewer,
)

logger = logging.getLogger(__name__)

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def _to_generic_media_item(result: Dict, media_type: str = "tv") -> MediaItem:
    """Maps a single TMDB result to a generic MediaItem."""
    poster_path = result.get("poster_path")
    backdrop_path = result.get("backdrop_path")

    if media_type == "tv":
        title_key, original_title_key, start_date_key = "name", "original_name", "first_air_date"
    else:
        title_key, original_title_key, start_date_key = "title", "original_title", "release_date"

    start_date_str = result.get(start_date_key)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None

    return MediaItem(
        id=result["id"],
        type="ANIME" if media_type == "tv" else "MOVIE",
        title=MediaTitle(
            romaji=result.get(title_key, ""),
            english=result.get(title_key, ""),
            native=result.get(original_title_key, ""),
        ),
        cover_image=MediaImage(
            large=f"{IMAGE_BASE_URL}{poster_path}" if poster_path else "",
            medium=f"{IMAGE_BASE_URL}{poster_path}" if poster_path else "",
        ),
        banner_image=f"{IMAGE_BASE_URL}{backdrop_path}" if backdrop_path else None,
        description=result.get("overview"),
        average_score=int(result.get("vote_average", 0) * 10),
        popularity=int(result.get("popularity", 0)),
        start_date=start_date,
        favourites=result.get("vote_count"),
        episodes=None,
        duration=None,
        genres=[],
        tags=[],
        studios=[],
        synonyms=[],
        next_airing=None,
        end_date=None,
        streaming_episodes={},
        user_status=None,
        trailer=None,
    )


def to_generic_search_result(data: Dict, media_type: str = "tv") -> MediaSearchResult:
    """Converts a raw TMDB search API response into a generic MediaSearchResult."""
    results = data.get("results", [])
    media_items = [_to_generic_media_item(item, media_type) for item in results]

    page_info = PageInfo(
        total=data.get("total_results", 0),
        current_page=data.get("page", 1),
        has_next_page=data.get("page", 1) < data.get("total_pages", 1),
        per_page=len(media_items),
    )
    return MediaSearchResult(page_info=page_info, media=media_items)


def _to_generic_character(cast_member: Dict) -> Character:
    """Maps a TMDB cast member to a generic Character."""
    profile_path = cast_member.get("profile_path")
    return Character(
        id=cast_member.get("id"),
        name=CharacterName(
            full=cast_member.get("name"), native=cast_member.get("original_name")
        ),
        image=CharacterImage(
            large=f"{IMAGE_BASE_URL}{profile_path}" if profile_path else "",
            medium=f"{IMAGE_BASE_URL}{profile_path}" if profile_path else "",
        ),
        description=cast_member.get("character"),
        favourites=int(cast_member.get("popularity", 0)),
    )


def to_generic_characters_result(data: Dict) -> Optional[CharacterSearchResult]:
    """Maps a TMDB credits response to a generic CharacterSearchResult."""
    cast = data.get("cast", [])
    characters = [_to_generic_character(member) for member in cast]
    return CharacterSearchResult(characters=characters, page_info=None)


def _to_generic_review(review_data: Dict) -> MediaReview:
    """Maps a TMDB review to a generic MediaReview."""
    author_details = review_data.get("author_details", {})
    avatar_path = author_details.get("avatar_path")

    if avatar_path and avatar_path.startswith("/https"):
        avatar_url = avatar_path[1:]
    elif avatar_path:
        avatar_url = f"{IMAGE_BASE_URL}{avatar_path}"
    else:
        avatar_url = None

    return MediaReview(
        body=review_data.get("content", ""),
        user=Reviewer(
            name=author_details.get("username", "Unknown"), avatar_url=avatar_url
        ),
    )


def to_generic_reviews_list(data: Dict) -> Optional[List[MediaReview]]:
    """Maps a TMDB reviews response to a list of generic MediaReview objects."""
    results = data.get("results", [])
    return [_to_generic_review(item) for item in results]


def to_generic_recommendations(data: Dict) -> Optional[List[MediaItem]]:
    """Maps a recommendations response to a list of MediaItems."""
    search_result = to_generic_search_result(data)
    return search_result.media if search_result else None


def to_generic_relations(data: Dict) -> Optional[List[MediaItem]]:
    """Maps a similar media response to a list of MediaItems."""
    search_result = to_generic_search_result(data)
    return search_result.media if search_result else None
