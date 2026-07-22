"""
Core data classes and the top-level recommend_songs orchestrator.

Data flow:
  UserRequest -> fetcher.fetch_songs_by_tags -> List[Song]
              -> ai_recommender.rank_and_explain -> List[(Song, float, str)]
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Song:
    """A real track retrieved from Last.fm."""
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
    """A natural language music request from the user."""
    text: str


def recommend_songs(request: UserRequest, k: int = 5) -> List[Tuple[Song, float, str]]:
    """
    Full RAG pipeline: retrieve real songs then rank and explain with Gemini.

    Returns top-k as (song, score, explanation) tuples.

    Steps:
      0. validate_request     — guard rail: reject non-music prompts early
      1. load_favorite_songs  — local favorites go first in the pool
      2. parse_tags           — Gemini extracts Last.fm search tags from request
      3. fetch_songs_by_tags  — Last.fm returns real tracks for those tags
      4. rank_and_explain     — Gemini scores and explains the combined pool
    """
    from ai_recommender import validate_request, parse_tags, rank_and_explain
    from fetcher import load_favorite_songs, fetch_songs_by_tags

    # Step 0: guard rail — reject off-topic requests before any API calls
    if not validate_request(request):
        raise ValueError("Request is not music-related")

    # Step 1: local favorites always enter the pool first
    favorites = load_favorite_songs()

    # Step 2: Gemini turns natural language into Last.fm search tags
    tags = parse_tags(request)

    # Step 3: fetch real tracks from Last.fm for each tag
    fetched = fetch_songs_by_tags(tags)

    # Step 4: merge (favorites first, no duplicates), then Gemini ranks
    seen_ids = {s.id for s in favorites}
    pool = favorites + [s for s in fetched if s.id not in seen_ids]

    return rank_and_explain(request, pool, k=k)
