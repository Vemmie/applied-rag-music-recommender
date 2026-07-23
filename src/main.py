"""Entry point — run as `python src/main.py` from the project root."""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from fetcher import save_favorite_song
from recommender import UserRequest, recommend_songs


def _prompt_save(results) -> None:
    """Ask the user if they want to save any results to favorites."""
    answer = input("Save to favorites? Enter result numbers (e.g. 1 3) or press Enter to skip: ").strip()
    if not answer:
        return
    saved = []
    for part in answer.split():
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(results):
                save_favorite_song(results[idx].song)
                saved.append(results[idx].song.title)
    if saved:
        print(f"Saved: {', '.join(saved)}\n")
    else:
        print("No valid numbers entered, nothing saved.\n")


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

        _prompt_save(results)


if __name__ == "__main__":
    main()
