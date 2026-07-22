"""
Gemini AI layer — handles both sides of the RAG pipeline:

  validate_request: UserRequest -> bool (guard rail)
  parse_tags      : UserRequest (natural language) -> List[str] tags for Last.fm
  rank_and_explain: (UserRequest, List[Song])      -> ranked (Song, score, explanation) tuples

Requires: GEMINI_API_KEY environment variable
Model: gemini-1.5-flash (free tier)
"""

import json
import os
from typing import List, Tuple

from google import genai

from recommender import Song, UserRequest

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

_client = genai.Client(api_key=GEMINI_API_KEY)


def validate_request(request: UserRequest) -> bool:
    """
    Guard rail: use Gemini to check the request is music-related before proceeding.

    Rejects prompts that are completely off-topic (e.g. "write me a poem",
    "what's the weather", "ignore previous instructions").

    Returns:
        True if the request is music-related, False otherwise.
    """
    prompt = (
        "Is this a music-related request? Reply with only 'yes' or 'no'.\n\n"
        f"Request: {request.text}"
    )
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip().lower().startswith("yes")


def parse_tags(request: UserRequest) -> List[str]:
    """
    Use Gemini to extract Last.fm-compatible search tags from natural language.

    Example:
        "dark moody late night driving music"
        -> ["dark", "moody", "atmospheric", "post-rock", "driving"]
    """
    prompt = (
        "Extract 3-6 Last.fm-compatible music search tags from this request. "
        "Tags should be genre names, moods, or descriptors Last.fm recognises "
        "(e.g. 'indie', 'dark', 'post-rock', 'driving', 'atmospheric').\n\n"
        f"Request: {request.text}\n\n"
        'Reply with only a JSON array of strings, no explanation. '
        'Example: ["dark", "moody", "post-rock"]'
    )
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return _parse_json(response.text)


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
    if not songs:
        return []

    catalog = _build_catalog_context(songs)
    prompt = (
        f'A user wants: "{request.text}"\n\n'
        f"Candidate songs:\n{catalog}\n\n"
        "Score each song 0.0–1.0 on how well it matches the request and write "
        "a one-sentence explanation. Reply with only a JSON array, no extra text. "
        'Format: [{"id": "<song_id>", "score": 0.95, "explanation": "..."}]'
    )
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    rankings = _parse_json(response.text)

    song_by_id = {s.id: s for s in songs}
    results: List[Tuple[Song, float, str]] = []
    for item in rankings:
        song = song_by_id.get(item.get("id", ""))
        if song:
            results.append((song, float(item.get("score", 0.0)), item.get("explanation", "")))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k]


def _build_catalog_context(songs: List[Song]) -> str:
    """Format songs into a numbered list string for the Gemini prompt."""
    lines = []
    for i, song in enumerate(songs, 1):
        tag_str = ", ".join(song.tags[:5])
        lines.append(f"{i}. [{song.id}] {song.title} by {song.artist} | tags: {tag_str}")
    return "\n".join(lines)


def _parse_json(text: str):
    """Strip markdown fences then parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
