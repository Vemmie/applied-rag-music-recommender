import pytest
from recommender import Song, UserRequest


@pytest.fixture
def sample_song():
    return Song(
        id="test::sample-track",
        title="Sample Track",
        artist="Sample Artist",
        genre="pop",
        mood="happy",
        tags=["pop", "upbeat", "energetic"],
        listeners=50000,
        url="https://www.last.fm/music/Sample+Artist/_/Sample+Track",
    )


@pytest.fixture
def music_request():
    return UserRequest("upbeat pop for a morning workout")
