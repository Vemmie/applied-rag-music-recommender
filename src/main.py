"""
Entry point for the Applied RAG Music Recommender.

Run:
    python -m src.main

Set environment variables before running:
    LASTFM_API_KEY=your_lastfm_key
    GEMINI_API_KEY=your_gemini_key
"""

from recommender import UserRequest, recommend_songs


def main() -> None:
    request = UserRequest("upbeat pop for a morning workout")

    # TODO: call recommend_songs and print results
    pass


if __name__ == "__main__":
    main()
