"""Entry point — run as `python src/main.py` from the project root."""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from recommender import UserRequest, recommend_songs


def main() -> None:
    """Interactive CLI loop — keeps prompting for music requests until the user quits."""
    print("Music Recommender  (type 'quit' to exit)\n")
    while True:
        text = input("What kind of music are you looking for? ").strip()
        if not text:
            continue
        if text.lower() in {"quit", "exit", "q"}:
            print("Bye!")
            break

        request = UserRequest(text)
        try:
            results = recommend_songs(request, k=5)
        except ValueError as e:
            print(f"Rejected: {e}\n")
            continue

        print(f"\nTop {len(results)} recommendations for: \"{request.text}\"\n")
        for i, rec in enumerate(results, 1):
            print(f"{i}. {rec.song.title} by {rec.song.artist}  "
                  f"(score: {rec.score:.2f}, confidence: {rec.confidence:.0%})")
            print(f"   {rec.explanation}")
            print(f"   {rec.song.url}\n")


if __name__ == "__main__":
    main()
