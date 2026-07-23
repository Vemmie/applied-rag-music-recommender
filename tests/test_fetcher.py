"""Unit tests for fetcher.py — no API calls required."""

import pytest
import fetcher


def test_load_returns_empty_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(fetcher, "_FAVORITES_CSV", tmp_path / "nonexistent.csv")
    assert fetcher.load_favorite_songs() == []


def test_save_then_load_roundtrip(tmp_path, monkeypatch, sample_song):
    monkeypatch.setattr(fetcher, "_FAVORITES_CSV", tmp_path / "songs.csv")
    fetcher.save_favorite_song(sample_song)
    songs = fetcher.load_favorite_songs()
    assert len(songs) == 1
    loaded = songs[0]
    assert loaded.id == sample_song.id
    assert loaded.title == sample_song.title
    assert loaded.artist == sample_song.artist
    assert loaded.listeners == sample_song.listeners


def test_tags_survive_csv_roundtrip(tmp_path, monkeypatch, sample_song):
    monkeypatch.setattr(fetcher, "_FAVORITES_CSV", tmp_path / "songs.csv")
    fetcher.save_favorite_song(sample_song)
    loaded = fetcher.load_favorite_songs()[0]
    assert loaded.tags == sample_song.tags


def test_save_skips_duplicate_id(tmp_path, monkeypatch, sample_song):
    monkeypatch.setattr(fetcher, "_FAVORITES_CSV", tmp_path / "songs.csv")
    fetcher.save_favorite_song(sample_song)
    fetcher.save_favorite_song(sample_song)
    assert len(fetcher.load_favorite_songs()) == 1


def test_fetch_returns_empty_without_api_key(monkeypatch):
    monkeypatch.setattr(fetcher, "LASTFM_API_KEY", "")
    assert fetcher.fetch_songs_by_tags(["pop", "rock"]) == []
