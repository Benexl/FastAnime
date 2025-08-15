import pytest
from httpx import Client, Response

from fastanime.core.config.model import TmdbConfig
from fastanime.libs.media_api.params import (
    MediaSearchParams,
    MediaRecommendationParams,
    MediaCharactersParams,
    MediaRelationsParams,
    MediaReviewsParams,
)
from fastanime.libs.media_api.tmdb.api import TmdbApi
from fastanime.libs.media_api.types import MediaType

TMDB_API_URL = "https://api.themoviedb.org/3"

@pytest.fixture
def tmdb_api():
    config = TmdbConfig(api_key="test_api_key")
    return TmdbApi(config, Client())

def test_search_media_success(tmdb_api, httpx_mock):
    """Test successful media search."""
    mock_response = {
        "page": 1,
        "results": [
            {
                "poster_path": "/jIhL6mlT7A9vugJvK3OTM6vws6z.jpg",
                "popularity": 29.78,
                "id": 1399,
                "backdrop_path": "/mUkuc2wyV9dHLG0D0Loaw5pO2s8.jpg",
                "vote_average": 7.91,
                "overview": "Seven noble families fight for control...",
                "first_air_date": "2011-04-17",
                "origin_country": ["US"],
                "genre_ids": [10765, 18, 10759, 9648],
                "original_language": "en",
                "vote_count": 1172,
                "name": "Game of Thrones",
                "original_name": "Game of Thrones",
            }
        ],
        "total_results": 1,
        "total_pages": 1,
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/search/tv?api_key=test_api_key&query=Game%20of%20Thrones&page=1&language=en-US",
        json=mock_response,
    )

    params = MediaSearchParams(query="Game of Thrones", type=MediaType.ANIME)
    result = tmdb_api.search_media(params)

    assert result is not None
    assert result.page_info.total == 1
    assert len(result.media) == 1
    assert result.media[0].id == 1399
    assert result.media[0].title.english == "Game of Thrones"

def test_search_media_empty_query(tmdb_api):
    """Test search with an empty query."""
    params = MediaSearchParams(query="")
    result = tmdb_api.search_media(params)
    assert result is None

def test_search_media_api_error(tmdb_api, httpx_mock):
    """Test search when the API returns an error."""
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/search/tv?api_key=test_api_key&query=Error&page=1&language=en-US",
        status_code=500,
    )
    params = MediaSearchParams(query="Error", type=MediaType.ANIME)
    result = tmdb_api.search_media(params)
    assert result is None


def test_get_recommendations(tmdb_api, httpx_mock):
    """Test getting recommendations for a media item."""
    media_id = 1399
    mock_response = {
        "page": 1,
        "results": [{"id": 1400, "name": "Another Show", "vote_average": 8.0, "popularity": 10}],
        "total_pages": 1,
        "total_results": 1
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/tv/{media_id}/recommendations?api_key=test_api_key&page=1&language=en-US",
        json=mock_response,
    )

    params = MediaRecommendationParams(id=media_id)
    result = tmdb_api.get_recommendation_for(params)
    assert result is not None
    assert len(result) == 1
    assert result[0].id == 1400

def test_get_characters(tmdb_api, httpx_mock):
    """Test getting characters for a media item."""
    media_id = 1399
    mock_response = {
        "cast": [{"id": 12795, "name": "Matthew McConaughey", "character": "Rust Cohle"}],
        "crew": [],
        "id": 46648
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/tv/{media_id}/credits?api_key=test_api_key&language=en-US",
        json=mock_response,
    )

    params = MediaCharactersParams(id=media_id)
    result = tmdb_api.get_characters_of(params)
    assert result is not None
    assert len(result.characters) == 1
    assert result.characters[0].name.full == "Matthew McConaughey"

def test_get_related(tmdb_api, httpx_mock):
    """Test getting related media for a media item."""
    media_id = 1399
    mock_response = {
        "page": 1,
        "results": [{"id": 1402, "name": "Similar Show", "vote_average": 7.5, "popularity": 12}],
        "total_pages": 1,
        "total_results": 1
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/tv/{media_id}/similar?api_key=test_api_key&language=en-US&page=1",
        json=mock_response,
    )

    params = MediaRelationsParams(id=media_id)
    result = tmdb_api.get_related_anime_for(params)
    assert result is not None
    assert len(result) == 1
    assert result[0].id == 1402

def test_get_reviews(tmdb_api, httpx_mock):
    """Test getting reviews for a media item."""
    media_id = 1399
    mock_response = {
        "id": 1399,
        "page": 1,
        "results": [{"author": "Cat Ellington", "author_details": {"username": "Cat Ellington"}, "content": "A masterpiece."}],
        "total_pages": 1,
        "total_results": 1
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{TMDB_API_URL}/tv/{media_id}/reviews?api_key=test_api_key&language=en-US&page=1",
        json=mock_response,
    )

    params = MediaReviewsParams(id=media_id)
    result = tmdb_api.get_reviews_for(params)
    assert result is not None
    assert len(result) == 1
    assert result[0].user.name == "Cat Ellington"
