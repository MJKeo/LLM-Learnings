#!/usr/bin/env python3

"""
Handles the flow of the game as it plays out
"""

from classes import Element, SpellType, Spell, Wizard
from prompts import WIZARD_GENERATOR_SYSTEM_PROMPT, SPELL_GENERATOR_SYSTEM_PROMPT
from schemas import WIZARD_GENERATION_SCHEMA, SPELL_GENERATION_SCHEMA
import ollama

def main():
    user_prompt = input("Prompt: ")
    messages = [
        {"role": "system", "content": WIZARD_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    response = ollama.chat(
        model="llama3.2", 
        messages=messages,
        format=WIZARD_GENERATION_SCHEMA,
        options={
            "temperature": 0.85,
            "num_predict": 180,
            "top_p": 0.85,
            "top_k": 40
        }
    )
    stats = response["message"]["content"]
    print("==== Wizard Stats ====")
    print(stats)

    spell_prompt = f"Wizard description:\n{user_prompt}\nWizard stats:\n{stats}"
    messages = [
        {"role": "system", "content": SPELL_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": spell_prompt}
    ]
    response = ollama.chat(
        model="llama3.2", 
        messages=messages,
        format=SPELL_GENERATION_SCHEMA,
        options={
            "temperature": 0.65,
            "num_predict": 275,
            "top_p": 0.85,
            "top_k": 40
        }
    )
    spells = response["message"]["content"]
    print("==== Wizard Spells ====")
    print(spells)

# Example usage:
if __name__ == "__main__":
    main()


# # Generation logic:
# • Name - whatever
# • Element - what is best fitting based on the description
# • Spells - create something that is partially balance and connects well with the description given
#     • The higher the value of a spell the more mana it should be
# • Attack - [40,100]
# • Defense - [40,100]
# • Health - [600, 1000]
# • Mana - [8,15]


# # Spell generation:
# • Name - whatever
# • Description - whatever
# • spell_type - Try and have a variety of these (unless the prompt really doesn't want it to be)
# • element - Whatever makes sense based on the prompts
# • value - as a % of the max value it can have
# • mana_cost - whatever makes sense based on the value generated

# Have a separate spell generator LLM and overall stats generator?
# Gain 2 mana per round