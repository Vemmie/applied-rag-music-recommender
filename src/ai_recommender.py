"""
Gemini AI layer — handles both sides of the RAG pipeline:

  parse_tags      : UserRequest (natural language) -> List[str] tags for Last.fm
  rank_and_explain: (UserRequest, List[Song])      -> ranked (Song, score, explanation) tuples

Requires: GEMINI_API_KEY environment variable
Model: gemini-2.0-flash (free tier)
"""

import os
from typing import List, Tuple
from recommender import Song, UserRequest

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def validate_request(request: UserRequest) -> bool:
    """
    Guard rail: use Gemini to check the request is music-related before proceeding.

    Rejects prompts that are completely off-topic (e.g. "write me a poem",
    "what's the weather", "ignore previous instructions").

    Returns:
        True if the request is music-related, False otherwise.
    """
    # TODO: prompt Gemini: "Is this a music-related request? Reply yes or no: {request.text}"
    # TODO: return True if response is "yes", False otherwise
    pass


def parse_tags(request: UserRequest) -> List[str]:
    """
    Use Gemini to extract Last.fm-compatible search tags from natural language.

    Example:
        "dark moody late night driving music"
        -> ["dark", "moody", "atmospheric", "post-rock", "driving"]
    """
    # TODO: prompt Gemini to return a JSON list of tags from request.text
    pass


def rank_and_explain(
    request: UserRequest,
    songs: List[Song],
    k: int = 5,
) -> List[Tuple[Song, float, str]]:
    """
    Use Gemini to rerank songs and write a plain-English explanation for each.

    Returns top-k as (Song, score, explanation) sorted by score descending —
    same shape as the original rule-based recommend_songs output.
    """
    # TODO: build prompt with request.text + _build_catalog_context(songs)
    # TODO: ask Gemini for JSON [{id, score, explanation}, ...]
    # TODO: match id back to Song objects, sort, slice top-k
    pass


def _build_catalog_context(songs: List[Song]) -> str:
    """Format songs into a numbered list string for the Gemini prompt."""
    # TODO: "1. Title by Artist | tags: tag1, tag2, ..."
    pass
