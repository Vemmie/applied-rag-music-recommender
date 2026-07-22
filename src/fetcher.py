"""Last.fm retrieval layer and local CSV catalog management.

Requires LASTFM_API_KEY (optional); fetch_songs_by_tags returns [] when absent.
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
    """Load all songs from the local favorites CSV; returns [] if the file doesn't exist."""
    if not _FAVORITES_CSV.exists():
        return []
    with open(_FAVORITES_CSV, newline="", encoding="utf-8") as f:
        return [
            Song(
                id=row["id"],
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                tags=row["tags"].split("|") if row["tags"] else [],
                listeners=int(row["listeners"] or 0),
                url=row["url"],
            )
            for row in csv.DictReader(f)
        ]


def save_favorite_song(song: Song) -> None:
    """Append a song to the favorites CSV; silently skips if the id already exists."""
    if any(s.id == song.id for s in load_favorite_songs()):
        return

    file_exists = _FAVORITES_CSV.exists()
    with open(_FAVORITES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        row = {k: v for k, v in vars(song).items() if k != "tags"}
        row["tags"] = "|".join(song.tags)
        writer.writerow(row)


def fetch_songs_by_tags(tags: List[str], limit_per_tag: int = 10) -> List[Song]:
    """Query Last.fm tag.getTopTracks for each tag; returns [] when LASTFM_API_KEY is not set."""
    if not LASTFM_API_KEY:
        return []

    seen: set = set()
    songs: List[Song] = []
    for tag in tags:
        for raw in _fetch_top_tracks_for_tag(tag, limit_per_tag):
            artist = raw.get("artist", {}).get("name", "") if isinstance(raw.get("artist"), dict) else ""
            mbid = raw.get("mbid") or f"{artist}::{raw.get('name', '')}"
            if mbid in seen:
                continue
            seen.add(mbid)
            try:
                songs.append(get_track_info(artist, raw["name"]))
            except Exception:
                pass
    return songs


def get_track_info(artist: str, title: str) -> Song:
    """Fetch full track metadata from Last.fm track.getInfo and return a Song."""
    resp = requests.get(
        LASTFM_BASE_URL,
        params={"method": "track.getInfo", "artist": artist, "track": title,
                "api_key": LASTFM_API_KEY, "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    return _build_song(resp.json().get("track", {}))


def _fetch_top_tracks_for_tag(tag: str, limit: int) -> List[dict]:
    """Raw Last.fm tag.getTopTracks call; returns a list of track dicts."""
    resp = requests.get(
        LASTFM_BASE_URL,
        params={"method": "tag.getTopTracks", "tag": tag,
                "api_key": LASTFM_API_KEY, "format": "json", "limit": limit},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("tracks", {}).get("track", [])


def _build_song(raw: dict) -> Song:
    """Map a Last.fm track dict to a Song; uses first toptag as genre, second as mood."""
    artist_field = raw.get("artist", {})
    artist = artist_field.get("name", "") if isinstance(artist_field, dict) else str(artist_field)
    title = raw.get("name") or raw.get("title", "")
    tag_names = [t["name"] for t in raw.get("toptags", {}).get("tag", []) if isinstance(t, dict)]

    return Song(
        id=raw.get("mbid") or f"{artist}::{title}",
        title=title,
        artist=artist,
        genre=tag_names[0] if tag_names else "",
        mood=tag_names[1] if len(tag_names) > 1 else "",
        tags=tag_names,
        listeners=int(raw.get("listeners", 0) or 0),
        url=raw.get("url", ""),
    )
