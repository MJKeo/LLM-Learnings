#!/usr/bin/env python3

"""
Handles the flow of the game as it plays out
"""

from classes import Element, EnemyWizard, SpellType, Spell, Wizard, Defend, Heal
from prompts import WIZARD_GENERATOR_SYSTEM_PROMPT, SPELL_GENERATOR_SYSTEM_PROMPT
from schemas import WIZARD_GENERATION_SCHEMA, SPELL_GENERATION_SCHEMA
from enemy_wizards import ENEMY_WIZARDS
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

def main2():
    # for ew in ENEMY_WIZARDS:
    #     print(f"attack: {ew.attack} defense: {ew.defense} health: {ew.health} healing: {ew.healing} arcane: {ew.arcane}")
    #     print(f"DM: {ew.damage_multiplier()} RD: {ew.damage_reduction()} HP: {ew.max_hp()} SM: {ew.starting_mana()} MPR: {ew.mana_per_round()}")
    #     print()


    print(ENEMY_WIZARDS[0])

# Example usage:
if __name__ == "__main__":
    main()
