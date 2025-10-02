#!/usr/bin/env python3

"""
Handles the flow of the game as it plays out
"""

import json
import random
import time
from typing import List

import ollama

from classes import EnemyWizard, Wizard, Action
from enemy_wizards import ENEMY_WIZARDS
from game_state import GameState, PlayerState
from prompts import WIZARD_GENERATOR_SYSTEM_PROMPT, SPELL_GENERATOR_SYSTEM_PROMPT, combat_system_prompt
from schemas import WIZARD_GENERATION_SCHEMA, SPELL_GENERATION_SCHEMA, ACTION_CHOICE_SCHEMA

MODEL = "llama3.2"


def main():
    enemy = random.choice(ENEMY_WIZARDS)
    print("==== Enemy Preview ====")
    print(enemy.preview)
    print()

    user_prompt = input("Describe your wizard: ")

    # Build wizard stats and moveset using LLMs
    wizard_stats = generate_wizard(user_prompt)
    spells = generate_spells(user_prompt, wizard_stats)
    wizard_stats["spells"] = spells
    print(spells)
    generated_wizard = Wizard.build_from_json(wizard_stats)

    # Create the game state
    game_state = GameState()
    player_1, player_2 = game_state.initialize(generated_wizard, enemy)

    print("==== Wizards Overview ====")
    print(player_1)
    print()
    print(player_2)
    print()

    print(f"{player_1.name} will be acting first each round")
    print()

    print("=== Starting Game State ===")
    print(game_state)
    print()

    # Let the user read over their stats real quick
    input("Press enter to continue...")

    # === MAIN GAME LOOP ===
    turn = 1
    while game_state.get_winner() is None:
        # Increment mana at the start of each round
        if turn > 1:
            game_state.increment_mana()

        print(f"=== Turn {turn} ===")
        # Generate actions in advance
        player_1_action = generate_action_choice(game_state, 0)
        player_2_action = generate_action_choice(game_state, 1)

        # Perform player 1 action
        player_1_action_result = game_state.perform_action(0, player_1_action)
        print(player_1_action_result)
        print()
        print(game_state)
        print()

        # Check if we have a winner after player 1 action
        if game_state.get_winner() is not None:
            break

        # Perform player 2 action
        player_2_action_result = game_state.perform_action(1, player_2_action)
        print(player_2_action_result)
        print()
        print(game_state)
        print()

        turn += 1
    
    # === GAME OVER ===
    print()
    print(f"============== Game Over ==============")
    print(f"{game_state.get_winner().name} wins!")




def generate_wizard(user_prompt) -> dict:
    print("Generating wizard stats...")
    messages = [
        {"role": "system", "content": WIZARD_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
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
            "keep_alive": "10m"
        },
    )
    return json.loads(response.get("message", {}).get("content"))

def generate_spells(user_prompt, wizard_stats) -> dict:
    print("Generating spells...")
    spell_prompt = f"Wizard description:\n{user_prompt}\nWizard stats:\n{wizard_stats}"
    messages = [
        {"role": "system", "content": SPELL_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": spell_prompt}
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
            "keep_alive": "10m"
        }
    )
    return json.loads(response.get("message", {}).get("content"))

def generate_action_choice(game_state: GameState, 
                            acting_wizard_index: int) -> Action:
    acting_wizard_state = game_state.player_states[acting_wizard_index]
    defender_wizard_state = game_state.player_states[1 - acting_wizard_index]
    print(f"Generating action choice for {acting_wizard_state.player.wizard.name}...")
    messages = [
        {"role": "system", "content": combat_system_prompt(acting_wizard_state, acting_wizard_index == 0)},
        {"role": "user", "content": battle_snapshot(game_state, acting_wizard_state, defender_wizard_state)}
    ]
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        format=ACTION_CHOICE_SCHEMA,
        options={
            "temperature": 0.75,
            "num_predict": 15,
            "top_p": 0.9,
            "top_k": 40,
            "keep_alive": "10m"
        }
    )
    result = json.loads(response.get("message", {}).get("content"))
    return acting_wizard_state.player.wizard.affordable_actions(acting_wizard_state.current_mana)[result["action"] - 1]


def battle_snapshot(game_state: GameState, acting_wizard_state: PlayerState, enemy_wizard_state: PlayerState) -> None:
    def _format_actions(actions: List[Action]) -> List[str]:
        if not actions:
            return ["  - (none)"]
        formatted = []
        for action in actions:
            overview = action.overview()
            if isinstance(overview, tuple):
                overview = " ".join(str(part) for part in overview)
            formatted.append(f"  - {overview}")
        return formatted

    acting_wizard_actions = "\n".join(
        f"{idx}- {action.overview()}"
        for idx, action in enumerate(
            acting_wizard_state.player.wizard.affordable_actions(acting_wizard_state.current_mana),
            start=1,
        )
    )
    enemy_wizard_actions = "\n- ".join(action.overview() for action in enemy_wizard_state.player.wizard.affordable_actions(enemy_wizard_state.current_mana))

    acting_wizard_active_effects = ", ".join(str(effect) for effect in acting_wizard_state.active_effects) or "(none)"

    enemy_wizard_active_effects = ", ".join(str(effect) for effect in enemy_wizard_state.active_effects) or "(none)"

    return f"""Your State:
- Health: {acting_wizard_state.current_health}/{acting_wizard_state.max_health}
- Mana: {acting_wizard_state.current_mana}
- Active Effects:
    {acting_wizard_active_effects}

Enemy State:
- Health: {enemy_wizard_state.current_health}/{enemy_wizard_state.max_health}
- Mana: {enemy_wizard_state.current_mana}
- Active Effects:
    {enemy_wizard_active_effects}

Enemy Available Actions:
- {enemy_wizard_actions or '  (none)'}

Choose ONE of the following actions to take:
{acting_wizard_actions or '  (none)'}

Make sure to follow your combat style: {acting_wizard_state.player.wizard.combat_style}"""

# Example usage:
if __name__ == "__main__":
    main()