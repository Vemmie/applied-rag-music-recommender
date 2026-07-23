# Original Project Details:

The original project was the _ai110-module3show-musicrecommendersimulation-starter_. This project used a deterministic algorithm to ran predefined user profies to recommend music in the csv database based on attributes of the song.  My old algorithm scored songs based on  **energy**, **genre**, and **mood** as the most meaningful signals, with **valence** and **acousticness** as supporting features. Based on the scoring of all the songs it would recommend the top k songs. 

# Title and Summary: 

**applied-rag-music-recommender** 

This new spin on the orignal project replaces the deterministic scoring algorithm with a RAG-based pipline powered by Gemini and Last.fm. The apporach allows for more diverse prompts and more natural language requests that the LLMs can extract meaning from to recommend songs from Last.fm or the songs the favorite_songs.csv. Each recommendation comes back with a match score, a confidence rating, and a one-sentence explanation of why it fits. Rather than the original rigid object with attributes on a very small set of songs. 

# Architecture Overview:

![Schema](../assets/schema.png)

The core architecture has a pipline with 4 steps. We use Gemini as a guard rail to stop prompt injections or block any non music related prompts. Then Gemini extracts 3 - 5 tags that are Last.fm compatible to fetch songs from the Last.fm API. Note if users were to not use Last.fm or not set up the key, there's a fall back and uses songs from the local `favorite_songs.csv` catalog. Note the **favorite_songs.csv** even allows users to add songs **not in Last.fm** or **unreleased songs** and **favorite_songs.csv** catalog is always loaded as the seed pool. Gemini reranks the full pool and returns the top-k songs each with a match score, confidence rating, and one-sentence explanation.

# Setup Instructions:

Clone the repo, create a virtual environment, and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys — a Last.fm key is optional, and if omitted the pipeline falls back to the local CSV catalog only:

```
GEMINI_API_KEY=your_gemini_key
LASTFM_API_KEY=your_lastfm_key
```

I recommend the "gemini-2.0-flash" model for higher limits.

Links:
1. https://www.last.fm/api/authentication
2. https://aistudio.google.com/api-keys

Run the app from the project root with `python src/main.py`.

# Sample Interactions:

```
Music Recommender  (type 'quit' to exit)

What kind of music are you looking for? upbeat pop for a morning workout

Top 5 recommendations for: "upbeat pop for a morning workout"

1. Levitating by Dua Lipa  (score: 0.97, confidence: 95%)
   Upbeat, high-energy pop with a driving beat perfect for a morning workout.
   https://www.last.fm/music/Dua+Lipa/_/Levitating

2. As It Was by Harry Styles  (score: 0.93, confidence: 91%)
   Energetic indie-pop with a bright, driving tempo that fits a morning run perfectly.
   https://www.last.fm/music/Harry+Styles/_/As+It+Was

3. Blinding Lights by The Weeknd  (score: 0.89, confidence: 88%)
   Synth-driven pop with a relentless beat that keeps energy high throughout a workout.
   https://www.last.fm/music/The+Weeknd/_/Blinding+Lights

What kind of music are you looking for? quit
Bye!
```

# Design Decisions:

The original project hard coded one was great for certain features of the song, the one issue was that it was heavily dependent on the size of the data.csv and also couldn't fully understand intent or conflicting wants. Switching to RAG lets the system handle free form natural language requests and pull in new songs dynamically from Last.fm rather than being limited to a fixed dataset.  Gemini handles both ends of the pipeline tag extraction and reranking so the "algorithm" is the prompt rather than a hand-tuned formula. The local CSV still acts as a curated seed catalog so recommendations work even without a Last.fm key. You can even right songs! or add songs so it doesn't always need the Last.fm key. One issue though is that it's no longer deterministic or simple. The old design was lightweight and probably used a lot less energy, compared the the current RAG implemntation. Since this project was to implment rag one trad off would be energy used per commute (TOKENS) and the determistic nature of the old one. In application since there could be a non-rag one for everyone and rag pipline for premium users for example.

# Testing Summary:

There are 17 unit tests and 8 integration tests organized under `tests/`. The unit tests use mocked Gemini responses so they run fast with no API key. They cover CSV roundtrips, duplicate prevention, tag pipe-splitting, JSON fence stripping, validate exact-match logic, rank ordering, and the k-limit. The integration tests hit the real Gemini API and verify the guard rail blocks non-music requests including four adversarial prompt injection strings, allows valid music requests, and that the full pipeline returns properly structured `Recommendation` objects. Run unit tests with `pytest -m "not integration"` and integration tests with `pytest -m integration`.

**Unit tests vs Inegration tests**
For those not familiar, the unit test mimics Gemini with mocks. The integration one uses real API calls.

**Manual Testing**
I tested out a few prompts to see if the guard rails work. Tested to see if the k limit worked. Lastly to see if the VIBEZ of the songs seemed right to me. 

_**NOTE**_: FREE TIERS ARE NOT THAT GREAT I HIT LIMITS PRETTY FAST AND THE RESULTS OF YOUR RECOMMENDATIONS MAY DEPEND ON YOUR MODEL.


# Reflection:

I used a process of human in the loop while using AI and collaborting with AI to make development smooth. AI really helps with boiler plate and giving functioning code; however, sometimes it miss understands intent and overcomplicate or oversimplify. AI is great for deriving meaning more than a deterministic scoring function. It trades predictability and efficiency for flexibility and understanding.  The guard rail ended up being more interesting than expected: putting the user text in `[USER INPUT]` tags and routing the classifier instruction through a separate system channel made a real difference in blocking injection attempts. If I were to continue down this project I would consider a rate recommendation systems to weight songs written back to `favorite_songs.csv` to personalize the seed catalog over time. For future applications that could use this pipeline it would probably have a real database instance instead of a .csv (probably a vector encoded one). Of course the free tier and premium tier that can use a non-rag or rag based recommendation system.  


