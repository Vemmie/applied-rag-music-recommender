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
    # TODO: step 0 — call validate_request(request); if False, raise ValueError("Request is not music-related")
    # TODO: implement remaining pipeline steps
    pass
