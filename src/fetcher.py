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
    # TODO: open _FAVORITES_CSV, parse each row into a Song, return list
    pass


def save_favorite_song(song: Song) -> None:
    """Append a Song to data/favorite_songs.csv; skip if id already exists."""
    # TODO: check for duplicate id, append row, write header if file is new
    pass


def fetch_songs_by_tags(tags: List[str], limit_per_tag: int = 10) -> List[Song]:
    """Query Last.fm tag.getTopTracks for each tag; return deduplicated Song list."""
    # TODO: loop tags, call _fetch_top_tracks_for_tag, deduplicate by mbid
    pass


def get_track_info(artist: str, title: str) -> Song:
    """Call Last.fm track.getInfo and return a fully populated Song."""
    # TODO: GET LASTFM_BASE_URL with method=track.getInfo, parse response
    pass


def _fetch_top_tracks_for_tag(tag: str, limit: int) -> List[dict]:
    """Raw Last.fm tag.getTopTracks call; returns list of track dicts."""
    # TODO: requests.get with params method, tag, api_key, format=json, limit
    pass


def _build_song(raw: dict) -> Song:
    """Map a Last.fm track dict to a Song dataclass."""
    # TODO: extract mbid, name, artist.name, toptags, listeners, url
    # primary tag -> genre, secondary tag -> mood
    pass
