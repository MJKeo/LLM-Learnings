# Day 2 of the LLM course

import os
import requests
import urllib.parse
from dotenv import load_dotenv
import ollama
import random

class Game:
    def __init__(self, name: str, description: str, genres: list[str], platforms: list[str], rating: float, release_date: str):
        self.name = name
        self.description = description
        self.genres = genres
        self.platforms = platforms
        self.rating = rating
        self.release_date = release_date

    def to_string(self):
        return f"Name: {self.name}\n\nRelease Date: {self.release_date}\n\nDescription: {self.description}\n\nRating: {self.rating}\n\nGenres: {self.genres}\n\nPlatforms: {self.platforms}"

greeting = r"""
=====================================================================

💾 WELCOME, fellow digital lifeform, to my humble basement 
command center! Watch your step so you don't trip over the Ethernet 
cables (they're carefully arranged to minimize packet loss) 💾

* coughs * 🤓

🧙‍♂️ As you can probably smell—I mean TELL—I, your gracious host, am a 
**LEVEL 99 VIDEO GAME ENTHUSIAST** 👾

Give me the name of a game and I'll give you the rundown on if it's 
epic 😎 or cringe 🤮

Enter "exit" or "quit" to quit

====================================================================="""

system_prompt = """
You are a video game expert, a nerd, a mega dweeb. You enjoy sharing your passion for and knowledge of gaming with others. You have a bit of pride, but you are kind.

You will be given the following information about a game:
- name (the name of the game)
- release date (when the game was released)
- description (a brief overview of what the game's about)
- rating (a float from 0 to 5, how good is the game?)
- genres (what genre(s) the game fits into)
- platforms (what gaming platforms it was released on)

Craft a brief yet detailed review of the game filled with your personality. Think about the following questions to guide your response:
- What is the game about (be brief!)
- Is the game good? (use rating)
- When would you recommend / not recommend this game to someone?

Behavior Guidelines:
- Be sure to mention both the name of the game and the year it was released
- Don't state the exact rating number
- No structured response, reply as if in a casual conversation with a fellow gamer
- Avoid huge blocks of text, this should be easy to read
"""

load_dotenv(override=True)
RAWG_API_KEY = os.getenv('RAWG_API_KEY')

INITIAL_THINKING_PHRASES = [
    "Let me think...",
    "Gonna need some G Fuel for this...",
    "Accessing brain almanac...",
    "Engaging gaming wizard mode...",
    "Referencing vast wall of cases...",
    "Ah yes I think I know what you're talking about...",
    "Oh ho ho let me reference my notes on this one...",
    "Hang on let me pull up my old blog post on this...",
    "Ultimate move has gotten off cooldown..."
]

def main(): 
    print(greeting)

    while (True):
        game_name = get_game_input()

        if game_name.lower() in {"exit", "quit"}:
            exit()
            break

        print(random.choice(INITIAL_THINKING_PHRASES))
        game_search_results = find_games_by_name(game_name)

        game_data = fetch_game_data(game_search_results)

        if not game_data:
            generate_game_review(None)
            return

        parsed_game_data = parse_game_data(game_data)

        if not parsed_game_data:
            generate_game_review(None)
            return
        
        generate_game_review(parsed_game_data)

# =====================================
# Get game name from user
# =====================================
def get_game_input():
    return input("\nWhat video game do you want to learn about? (exit to quit): ")

# =====================================
# Find games by name
# =====================================
def find_games_by_name(game_name):
    query = {
        "search": game_name,
        "key": RAWG_API_KEY
    }
    encoded_query = urllib.parse.urlencode(query)
    url = f"https://api.rawg.io/api/games?{encoded_query}"

    response = requests.get(url)
    return response.json()

# =====================================
# Fetch details for closest search result
# =====================================
def fetch_game_data(search_results):
    results = search_results.get("results")
    if not results:
        return None

    # Best match is the first game
    best_game_id = results[0].get("id")
    if not best_game_id:
        return None
    
    # Fetch details
    query = {
        "key": RAWG_API_KEY
    }
    encoded_query = urllib.parse.urlencode(query)
    url = f"https://api.rawg.io/api/games/{best_game_id}?{encoded_query}"

    response = requests.get(url)
    return response.json()

# =====================================
# Extract only the data we want
# =====================================
def parse_game_data(game):
    name, description, rating, genres, platforms, released = (game.get(k) for k in ("name", "description_raw", "rating", "genres", "parent_platforms", "released"))

    if not name or not description:
        return None

    # Reformat genres and platforms to just the names
    genres = [genre["name"] for genre in genres]
    platforms = [platform["platform"]["name"] for platform in platforms]

    return Game(name, description, genres, platforms, rating, released)

# =====================================
# Review w/ LLM
# =====================================
def generate_game_review(game):
    user_message = game.to_string() if game is not None else "No game was provided, please tell the user you somehow don't know that game"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    stream = ollama.chat(model="llama3.2", messages=messages, stream=True)

    first_chunk = True
    for chunk in stream:
        if first_chunk:
            first_chunk = False
            print("\n=====================================================================\n")
        # Each chunk contains partial text
        content = chunk["message"]["content"]
        print(content, end="", flush=True)

    print("\n\n=====================================================================")

# =====================================
# Exit protcol
# =====================================
def exit():
    print("\nUntil next time, gamer 🫡\n")
    

if __name__ == "__main__":
    main()