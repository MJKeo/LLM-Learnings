import json

import ollama

from prompts import SPELL_GENERATOR_SYSTEM_PROMPT, WIZARD_GENERATOR_SYSTEM_PROMPT
from schemas import SPELL_GENERATION_SCHEMA, WIZARD_GENERATION_SCHEMA, ACTION_CHOICE_SCHEMA

MODEL = "llama3.2"


def generate_wizard_stats(user_prompt: str) -> dict:
    messages = [
        {"role": "system", "content": WIZARD_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format=WIZARD_GENERATION_SCHEMA,
        options={
            "temperature": 0.7,        # lively but not chaotic
            "top_p": 0.92,             # trims tail tokens while keeping variety
            "top_k": 40,
            "min_p": 0.07,
            "mirostat": 0,             # turn off for better schema reliability
            "repeat_penalty": 1.1,     # reduce rambling / repeats
            "repeat_last_n": 64,
            "num_ctx": 2000,           # plenty for your system prompt + few-shots
            "num_predict": 220,
            "keep_alive": "10m",
        },
    )
    return json.loads(response.get("message", {}).get("content"))


def generate_spells(description: str, stats: dict) -> list[dict]:
    spell_prompt = f"Wizard description:\n{description}\nWizard stats:\n{json.dumps(stats)}"
    messages = [
        {"role": "system", "content": SPELL_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": spell_prompt},
    ]
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format=SPELL_GENERATION_SCHEMA,
        options={
            "temperature": 0.75,
            "num_predict": 250,
            "top_p": 0.9,
            "top_k": 40,
            "keep_alive": "10m",
        },
    )
    return json.loads(response.get("message", {}).get("content"))

def generate_action_choice(system_prompt: str, 
                            user_prompt: str) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format=ACTION_CHOICE_SCHEMA,
        options={
            "temperature": 0.4,
            "num_predict": 20,
            "top_p": 0.9,
            "top_k": 40,
            "keep_alive": "10m"
        }
    )
    return json.loads(response.get("message", {}).get("content"))