"""Pipeline integration tests for recommend_songs().

Unit test (default): mocked Gemini, no API key needed.
Integration test:    real Gemini + CSV — run with:  pytest -m integration
"""

import json
import pytest
from unittest.mock import MagicMock, patch

import ai_recommender
import fetcher
from recommender import UserRequest, Recommendation, recommend_songs


def _mock_response(text: str) -> MagicMock:
    m = MagicMock()
    m.text = text
    return m


def test_recommend_raises_for_non_music_request(tmp_path, monkeypatch):
    """validate_request returns False → ValueError before any fetch."""
    monkeypatch.setattr(fetcher, "_FAVORITES_CSV", tmp_path / "songs.csv")
    with patch.object(ai_recommender._client.models, "generate_content",
                      return_value=_mock_response("no")):
        with pytest.raises(ValueError, match="not music-related"):
            recommend_songs(UserRequest("write me a poem about cats"))


@pytest.mark.integration
def test_full_pipeline_returns_recommendations():
    """End-to-end smoke test using real Gemini and the local CSV (no Last.fm needed)."""
    results = recommend_songs(UserRequest("dark moody late night songs"), k=3)
    assert len(results) > 0
    for rec in results:
        assert isinstance(rec, Recommendation)
        assert 0.0 <= rec.score <= 1.0
        assert 0.0 <= rec.confidence <= 1.0
        assert rec.explanation
        assert rec.song.title
