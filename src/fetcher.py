"""
Last.fm API retrieval layer.

Responsibilities:
  - load_favorite_songs  : load user's saved songs from data/favorite_songs.csv
  - save_favorite_song   : append a Song to data/favorite_songs.csv
  - fetch_songs_by_tags  : query Last.fm for real tracks by tag
  - get_track_info       : fetch full metadata for a single track
  - _build_song          : map a Last.fm API response dict to a Song dataclass

Requires: LASTFM_API_KEY environment variable
"""

import csv
import os
import requests
from pathlib import Path
from typing import List
from recommender import Song

_DATA_DIR = Path(__file__).parent.parent / "data"
_FAVORITES_CSV = _DATA_DIR / "favorite_songs.csv"
_CSV_FIELDNAMES = ["id", "title", "artist", "genre", "mood", "tags", "listeners", "url"]

LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY", "")


def load_favorite_songs() -> List[Song]:
    """Load saved favorites from data/favorite_songs.csv."""
    if not _FAVORITES_CSV.exists():
        return []
    songs = []
    with open(_FAVORITES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(Song(
                id=row["id"],
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                tags=row["tags"].split("|") if row["tags"] else [],
                listeners=int(row["listeners"]) if row["listeners"] else 0,
                url=row["url"],
            ))
    return songs


def save_favorite_song(song: Song) -> None:
    """Append a Song to data/favorite_songs.csv; skip if id already exists."""
    existing = load_favorite_songs()
    if any(s.id == song.id for s in existing):
        return

    file_exists = _FAVORITES_CSV.exists()
    with open(_FAVORITES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "tags": "|".join(song.tags),
            "listeners": song.listeners,
            "url": song.url,
        })


def fetch_songs_by_tags(tags: List[str], limit_per_tag: int = 10) -> List[Song]:
    """Query Last.fm tag.getTopTracks for each tag; return deduplicated Song list.

    Falls back to an empty list (so only favorites are used) when LASTFM_API_KEY
    is not set.
    """
    if not LASTFM_API_KEY:
        return []
    seen_ids: set = set()
    songs: List[Song] = []
    for tag in tags:
        raw_tracks = _fetch_top_tracks_for_tag(tag, limit_per_tag)
        for raw in raw_tracks:
            artist_name = raw.get("artist", {}).get("name", "") if isinstance(raw.get("artist"), dict) else ""
            track_name = raw.get("name", "")
            mbid = raw.get("mbid") or f"{artist_name}::{track_name}"
            if mbid in seen_ids:
                continue
            seen_ids.add(mbid)
            try:
                song = get_track_info(artist_name, track_name)
                songs.append(song)
            except Exception:
                pass
    return songs


def get_track_info(artist: str, title: str) -> Song:
    """Call Last.fm track.getInfo and return a fully populated Song."""
    resp = requests.get(LASTFM_BASE_URL, params={
        "method": "track.getInfo",
        "artist": artist,
        "track": title,
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return _build_song(data.get("track", {}))


def _fetch_top_tracks_for_tag(tag: str, limit: int) -> List[dict]:
    """Raw Last.fm tag.getTopTracks call; returns list of track dicts."""
    resp = requests.get(LASTFM_BASE_URL, params={
        "method": "tag.getTopTracks",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit,
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("tracks", {}).get("track", [])


def _build_song(raw: dict) -> Song:
    """Map a Last.fm track dict to a Song dataclass."""
    artist_field = raw.get("artist", {})
    artist = artist_field.get("name", "") if isinstance(artist_field, dict) else str(artist_field)
    title = raw.get("name") or raw.get("title", "")
    mbid = raw.get("mbid") or f"{artist}::{title}"

    toptags = raw.get("toptags", {}).get("tag", [])
    tag_names = [t["name"] for t in toptags if isinstance(t, dict) and "name" in t]

    genre = tag_names[0] if len(tag_names) > 0 else ""
    mood = tag_names[1] if len(tag_names) > 1 else ""

    return Song(
        id=mbid,
        title=title,
        artist=artist,
        genre=genre,
        mood=mood,
        tags=tag_names,
        listeners=int(raw.get("listeners", 0) or 0),
        url=raw.get("url", ""),
    )
