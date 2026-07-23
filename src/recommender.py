"""Core data classes and the top-level recommend_songs orchestrator.

Pipeline: validate -> load CSV -> parse tags -> fetch Last.fm -> rank with Gemini.
"""

from dataclasses import dataclass
from typing import List, NamedTuple


@dataclass
class Song:
    """A music track — either from the local CSV or retrieved from Last.fm."""

    id: str
    title: str
    artist: str
    genre: str
    mood: str
    tags: List[str]
    listeners: int
    url: str


@dataclass
class UserRequest:
    """A natural-language music request from the user."""

    text: str


class Recommendation(NamedTuple):
    """A ranked song result with match score, AI confidence, and explanation."""

    song: Song
    score: float
    confidence: float
    explanation: str


def recommend_songs(request: UserRequest, k: int = 5) -> List[Recommendation]:
    """Run the full RAG pipeline; raises ValueError if the request isn't music-related.

    Imports are deferred to avoid circular imports with fetcher and ai_recommender.
    """
    from ai_recommender import validate_request, parse_tags, rank_and_explain
    from fetcher import load_favorite_songs, fetch_songs_by_tags

    if not validate_request(request):
        raise ValueError("Request is not music-related")

    favorites = load_favorite_songs()
    tags = parse_tags(request)
    fetched = fetch_songs_by_tags(tags)

    seen_ids = {s.id for s in favorites}
    pool = favorites + [s for s in fetched if s.id not in seen_ids]

    return rank_and_explain(request, pool, k=k)
