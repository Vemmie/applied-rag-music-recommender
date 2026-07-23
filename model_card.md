# What are the limitations or biases in your system?

There are 100% limitations in my system, the biggest one being TOKEN usage. For a company providing a service like this would not be sustainable as you are using a LLM take consumes tokens per request costing you money for this recommendation system. Of course AI can't truly know what a user preference is through works to recommend songs. I notice it does basis towards using the favorite_songs.csv, probably in the future there should be a feature to turn off and on if favorite_songs.csv is the in the pool of songs to be choosen from. 

# Could your AI be misused, and how would you prevent that?

Since the AI is connected to the internet I thought the biggest the problem would be prompt injections. I added a guardrail to protect again those injections or non-music related prompts. With some testing it did seem to do the job. I'm pretty sure if a user spent more time with the sole goal of breaking I'm pretty sure they can. However, for the current scope I thought it did pretty good.

# What surprised you while testing your AI's reliability?

It gave not bad recommendations. The graud rails were holding up and the AI's reliability did produce results from Last.fm and csv provided which I though was pretty awesome seeing it all come to place. The AI suggested routing the classifier's system instruction through a separate `system_instruction` channel in the Gemini API rather than embedding it in the user message, and wrapping the user input in `[USER INPUT]` delimiters with an exact `== "yes"` match check. That combination made a real difference when I tested it against adversarial inputs — it held up a lot better than just putting everything in one prompt would have.

# Describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect.

I used Claude Code heavily throughout this project, mostly as a pairing partner to implement the pipeline, debug API issues, and refactor code. The workflow was pretty human-in-the-loop. I'd describe what I wanted, the AI would produce working code, and I'd push back or redirect when it missed the intent. Reading through the lines of code to see if make sense to make sure the code did not smell. Some manaul edits here and there. From planning to coding AI was used.

One genuinely helpful suggestion was the prompt injection defense design. Which is mention in the AI's reliability question. TLDR the `system_instruction` gave a lot better security than just a `role_prompt` before the user's input. 

One instance where it was flawed was overcomplicating request. (Which to be far could have used better and stricter prompting). One example AI generated very verbose docstrings for every function, which took up way more space than was useful for a project this size. I had to explicitly correct it and ask for 1–3 line docstrings instead. It did fix it immediately, definitely results to the very verbose or over simplified code at times.