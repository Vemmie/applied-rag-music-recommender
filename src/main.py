"""
Entry point for the Applied RAG Music Recommender.

Run:
    python src/main.py          (from project root)

Set environment variables in applied-rag-music-recommender/.env:
    LASTFM_API_KEY=your_lastfm_key
    GEMINI_API_KEY=your_gemini_key
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from recommender import UserRequest, recommend_songs


def main() -> None:
    request = UserRequest("upbeat pop for a morning workout")

    try:
        results = recommend_songs(request, k=5)
    except ValueError as e:
        print(f"Rejected: {e}")
        return

    print(f"Top {len(results)} recommendations for: \"{request.text}\"\n")
    for i, (song, score, explanation) in enumerate(results, 1):
        print(f"{i}. {song.title} by {song.artist}  (score: {score:.2f})")
        print(f"   {explanation}")
        print(f"   {song.url}")
        print()


if __name__ == "__main__":
    main()
