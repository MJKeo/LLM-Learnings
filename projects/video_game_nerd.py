#!/usr/bin/env python3
"""
Video Game Nerd - An interactive game review assistant

This program allows users to get AI-powered reviews of video games by:
1. Searching for games using the RAWG API
2. Fetching detailed game information
3. Generating personalized reviews using Ollama LLM
"""

import os
import requests
from dotenv import load_dotenv
import ollama
import random
import threading

class VideoGame:
    """Represents a video game with all its metadata"""
    
    def __init__(self, name: str, description: str, genres: list[str], platforms: list[str], rating: float, release_date: str):
        self.name = name
        self.description = description
        self.genres = genres
        self.platforms = platforms
        self.rating = rating
        self.release_date = release_date

    def format_for_llm(self) -> str:
        """Format game data as a string for LLM processing"""
        return f"""Name: {self.name}

Release Date: {self.release_date}

Description: {self.description}

Rating: {self.rating}

Genres: {self.genres}

Platforms: {self.platforms}"""

# Application constants
WELCOME_MESSAGE = r"""
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

LLM_SYSTEM_PROMPT = """
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

# Load environment variables
load_dotenv(override=True)
RAWG_API_KEY = os.getenv('RAWG_API_KEY')

# Create a global HTTP session for connection reuse and better performance
api_session = requests.Session()
api_session.headers.update({'User-Agent': 'VideoGameNerd/1.0'})

# Global progress indicator variables (shared between main and review generation)
progress_event = None
progress_thread = None

# Personality phrases to show while processing
THINKING_PHRASES = [
    "Let me think",
    "Gonna need some G Fuel for this",
    "Accessing brain almanac",
    "Engaging gaming wizard mode",
    "Referencing vast wall of cases",
    "Ah yes I think I know what you're talking about",
    "Oh ho ho let me reference my notes on this one",
    "Hang on let me pull up my old blog post on this",
    "Ultimate move has gotten off cooldown"
]

def main():
    """Main application loop - handles user interaction and game review workflow"""
    print(WELCOME_MESSAGE)

    while True:
        try:
            # Get user input and handle exit commands
            game_name = get_user_input()
            if is_exit_command(game_name):
                show_goodbye_message()
                return
            
            # Process the game request
            process_game_request(game_name)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            return
        except Exception as e:
            print(f"\nOops! Something went wrong: {e}")
            print("Let's try again...")


def process_game_request(game_name: str) -> None:
    """Handle the complete workflow for a single game request"""
    # Show thinking phrase and start progress indicator
    show_thinking_phrase()
    start_progress_indicator()
    
    try:
        # Fetch game data from API
        game_data = fetch_complete_game_data(game_name)
        
        # Generate and display review
        if game_data:
            generate_and_display_review(game_data)
        else:
            generate_and_display_review(None)  # Game not found
            
    finally:
        # Always stop progress indicator
        stop_progress_indicator()

def get_user_input() -> str:
    """Get game name input from user"""
    return input("\nWhat video game do you want to learn about? (exit to quit): ")

def is_exit_command(user_input: str) -> bool:
    """Check if user wants to exit the application"""
    return user_input.lower().strip() in {"exit", "quit"}

def show_thinking_phrase() -> None:
    """Display a random thinking phrase to show personality"""
    phrase = random.choice(THINKING_PHRASES)
    print(f"\n{phrase}", end="", flush=True)

def show_goodbye_message() -> None:
    """Display farewell message to user"""
    print("\nUntil next time, gamer 🫡\n")

def start_progress_indicator() -> None:
    """Start the progress dots thread for visual feedback"""
    global progress_event, progress_thread
    progress_event = threading.Event()
    progress_thread = threading.Thread(target=show_progress_dots, args=(progress_event,))
    progress_thread.daemon = True
    progress_thread.start()

def stop_progress_indicator() -> None:
    """Stop the progress dots thread"""
    global progress_event, progress_thread
    if progress_event and progress_thread:
        progress_event.set()
        progress_thread.join(timeout=1)

def fetch_complete_game_data(game_name: str) -> VideoGame | None:
    """Fetch complete game data from RAWG API - search then get details"""
    # Step 1: Search for games by name
    search_results = search_games_by_name(game_name)
    if not search_results:
        return None
    
    # Step 2: Get detailed information for the best match
    game_details = fetch_game_details(search_results)
    if not game_details:
        return None
    
    # Step 3: Parse and return structured game data
    return parse_raw_game_data(game_details)

def search_games_by_name(game_name: str) -> dict | None:
    """Search for games using RAWG API search endpoint"""
    search_params = {
        "search": game_name,
        "key": RAWG_API_KEY
    }
    
    try:
        response = api_session.get(
            "https://api.rawg.io/api/games", 
            params=search_params, 
            timeout=(3, 10)
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"\nError searching for games: {e}")
        return None

def fetch_game_details(search_results: dict) -> dict | None:
    """Fetch detailed information for the best matching game"""
    results = search_results.get("results", [])
    if not results:
        return None

    # Get the first (best) match
    best_match = results[0]
    game_id = best_match.get("id")
    if not game_id:
        return None
    
    # Fetch detailed game information
    detail_params = {"key": RAWG_API_KEY}
    
    try:
        response = api_session.get(
            f"https://api.rawg.io/api/games/{game_id}",
            params=detail_params,
            timeout=(3, 10)
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"\nError fetching game details: {e}")
        return None

def parse_raw_game_data(raw_data: dict) -> VideoGame | None:
    """Parse raw API data into a structured VideoGame object"""
    # Extract required fields
    name = raw_data.get("name")
    description = raw_data.get("description_raw")
    rating = raw_data.get("rating")
    genres_data = raw_data.get("genres", [])
    platforms_data = raw_data.get("parent_platforms", [])
    release_date = raw_data.get("released")
    
    # Validate required fields
    if not name or not description:
        return None
    
    # Parse genres and platforms into clean lists
    clean_genres = extract_genre_names(genres_data)
    clean_platforms = extract_platform_names(platforms_data)
    
    return VideoGame(
        name=name,
        description=description,
        genres=clean_genres,
        platforms=clean_platforms,
        rating=rating,
        release_date=release_date
    )

def extract_genre_names(genres_data: list) -> list[str]:
    """Extract genre names from API response"""
    if not genres_data:
        return []
    return [genre.get("name", "") for genre in genres_data if genre.get("name")]

def extract_platform_names(platforms_data: list) -> list[str]:
    """Extract platform names from API response"""
    if not platforms_data:
        return []
    return [
        platform.get("platform", {}).get("name", "") 
        for platform in platforms_data 
        if platform.get("platform", {}).get("name")
    ]

def generate_and_display_review(game: VideoGame | None) -> None:
    """Generate and display an AI-powered game review"""
    # Prepare the message for the LLM
    user_message = create_llm_message(game)
    
    # Create the conversation context
    conversation = [
        {"role": "system", "content": LLM_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    # Generate and stream the review
    stream_llm_response(conversation)

def create_llm_message(game: VideoGame | None) -> str:
    """Create the user message for LLM based on game data"""
    if game is None:
        return "No game was provided, please tell the user you somehow don't know that game"
    return game.format_for_llm()

def stream_llm_response(conversation: list[dict]) -> None:
    """Stream the LLM response with progress indicators"""
    try:
        # Start streaming the response
        stream = ollama.chat(model="llama3.2", messages=conversation, stream=True)
        
        # Extra variable to check if we've started streaming the response yet
        is_first_chunk = True
        
        # Stream and display each chunk
        for chunk in stream:
            # If this is the first chunk then end the progress indicator
            if is_first_chunk:
                is_first_chunk = False
                stop_progress_indicator
                print("\n\n=====================================================================\n")
            
            content = chunk.get("message", {}).get("content", "")
            if content:
                print(content, end="", flush=True)
        
        # Display the response footer
        print("\n\n=====================================================================")
        
    except Exception as e:
        print(f"\n\nError generating review: {e}")
        print("\n=====================================================================")

def show_progress_dots(stop_event: threading.Event) -> None:
    """Show animated dots every 0.5 seconds until stop_event is set"""
    while not stop_event.is_set():
        print(".", end="", flush=True)
        stop_event.wait(0.5)  # Wait 0.5 seconds or until event is set

# Application entry point
if __name__ == "__main__":
    main()