import json

import ollama

from prompts import SPELL_GENERATOR_SYSTEM_PROMPT, WIZARD_GENERATOR_SYSTEM_PROMPT
from schemas import SPELL_GENERATION_SCHEMA, WIZARD_GENERATION_SCHEMA

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
            "temperature": 0.85,
            "num_predict": 128,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 1400,
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
            "num_predict": 225,
            "top_p": 0.9,
            "top_k": 40,
            "keep_alive": "10m",
        },
    )
    return json.loads(response.get("message", {}).get("content"))