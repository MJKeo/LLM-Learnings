"""
Central game state tracking for the wizard prompt battle.

This module exposes a single ``game_state`` instance that can be imported
anywhere in the project to inspect or mutate the current match. The data
structures capture both player snapshots and the action history so far.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union

from classes import ActionTarget, ActionType, SpellType, Wizard, Action


class StatusEffectType(str, Enum):
    """Classifies an active effect."""

    DEFENSE = "defense"
    BUFF = "buff"
    DEBUFF = "debuff"


@dataclass
class StatusEffect:
    """Represents a single status effect on a player."""

    name: str
    effect_type: StatusEffectType
    value: float
    remaining_turns: int

    @property
    def is_buff(self) -> bool:
        return self.effect_type is StatusEffectType.BUFF

    @property
    def is_debuff(self) -> bool:
        return self.effect_type is StatusEffectType.DEBUFF

    @property
    def is_defense(self) -> bool:
        return self.effect_type is StatusEffectType.DEFENSE

    def __str__(self) -> str:
        return (
            f"{self.name}"
            f" [{self.effect_type}]"
            f" value={self.value}"
            f" turns={self.remaining_turns}"
        )


@dataclass
class Player:
    """Wraps a wizard with an assigned player identifier."""

    id: int
    wizard: Wizard


@dataclass
class PlayerState:
    """Snapshot of a player's current state."""

    player: Player
    max_health: int
    current_health: int
    current_mana: int
    active_effects: List[StatusEffect] = field(default_factory=list)

    def buffs(self) -> List[StatusEffect]:
        return [effect for effect in self.active_effects if effect.is_buff]

    def debuffs(self) -> List[StatusEffect]:
        return [effect for effect in self.active_effects if effect.is_debuff]

    def defenses(self) -> List[StatusEffect]:
        return [effect for effect in self.active_effects if effect.is_defense]

    def __str__(self) -> str:
        return (
            f"{self.player.wizard.name}: "
            f"HP {self.current_health}/{self.max_health}, "
            f"Mana {self.current_mana}, "
            f"Effects: {self._effects_summary()}"
        )

    def _effects_summary(self) -> str:
        if not self.active_effects:
            return "(none)"
        return ", ".join(str(effect) for effect in self.active_effects)


@dataclass
class ActionRecord:
    """Stores the outcome of a single action taken in the match."""

    actor_id: int  # 0 for player1, 1 for player2
    type: ActionType
    target: ActionTarget
    result: str


class EffectGroup(Enum):
    BUFFS_AND_DEBUFFS = 1
    DEFENSES = 2

    def includes(self, effect: StatusEffect) -> bool:
        if self is EffectGroup.BUFFS_AND_DEBUFFS:
            return effect.is_buff or effect.is_debuff
        if self is EffectGroup.DEFENSES:
            return effect.is_defense
        return False


class GameState:
    """Tracks the full state of an in-progress match."""

    def __init__(self) -> None:
        self.player_states: List[Player] = []
        self.action_log: List[ActionRecord] = []

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def initialize(
        self,
        wizard1: Wizard,
        wizard2: Wizard,
    ) -> List[Wizard]:
        """Reset the game state with fresh player snapshots."""

        assigned_order = [wizard1, wizard2]
        random.shuffle(assigned_order)

        self.player_states = []
        for index, wizard in enumerate(assigned_order):
            max_hp = wizard.max_hp()
            self.player_states.append(
                PlayerState(
                    player=Player(id=index, wizard=wizard),
                    max_health=max_hp,
                    current_health=max_hp,
                    current_mana=wizard.starting_mana(),
                )
            )

        self.action_log.clear()
        return [state.player.wizard for state in self.player_states]

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------
    def change_health(self, player: Player, delta: int) -> int:
        player_state = self.player_states[player.id]
        player_state.current_health = max(0, min(player_state.max_health, player_state.current_health + delta))
        return player_state.current_health

    def set_health(self, player: Player, value: int) -> int:
        player_state = self.player_states[player.id]
        player_state.current_health = max(0, min(player_state.max_health, value))
        return player_state.current_health

    def change_mana(self, player: Player, delta: int) -> int:
        player_state = self.player_states[player.id]
        player_state.current_mana = max(0, player_state.current_mana + delta)
        return player_state.current_mana

    def set_mana(self, player: Player, value: int) -> int:
        player_state = self.player_states[player.id]
        player_state.current_mana = max(0, value)
        return player_state.current_mana

    def add_status_effect(
        self,
        player: Player,
        effect: StatusEffect,
    ) -> None:
        player_state = self.player_states[player.id]
        for active_effect in player_state.active_effects:
            if active_effect.name == effect.name:
                active_effect.remaining_turns = effect.remaining_turns
                return

        player_state.active_effects.append(effect)

    def clear_expired_effects(self, player: Player) -> None:
        player_state = self.player_states[player.id]
        player_state.active_effects = [effect for effect in player_state.active_effects if effect.remaining_turns > 0]

    def tick_effects(self) -> None:
        """Reduce remaining turns for all active effects by one."""

        for player_state in self.player_states:
            for effect in player_state.active_effects:
                effect.remaining_turns = max(0, effect.remaining_turns - 1)

    def log_action(self, record: ActionRecord) -> None:
        self.action_log.append(record)

    def perform_action(self, actor_index: int, action: Action) -> Optional[dict]:
        if actor_index not in (0, 1):
            raise ValueError("actor_index must be 0 or 1")

        actor_state = self.player_states[actor_index]
        defender_state = self.player_states[1 - actor_index]

        if action.mana_cost() > actor_state.current_mana:
            raise ValueError("Not enough mana to perform action")

        result = action.perform_action()

        if not result.get("succeeded", False):
            self.log_action(ActionRecord(actor_index, action.action_type, action.action_target(), "Failed :("))
            self._decay_effects(actor_index)
            return action.failure_announcement(actor_state.player.wizard)

        actor_state.current_mana = max(0, actor_state.current_mana - action.mana_cost())

        final_action_value = result.get("value")

        match result.get("action_type"):
            case ActionType.HEAL:
                healed = self._apply_heal(actor_state, int(result["value"]))
                final_action_value = healed
                self.log_action(ActionRecord(actor_index, ActionType.HEAL, ActionTarget.SELF, f"Healed {healed}"))
            case ActionType.DEFEND:
                self._apply_status(
                    actor_state,
                    StatusEffect(
                        name=action.element.name,
                        effect_type=StatusEffectType.DEFENSE,
                        value=0.0,
                        remaining_turns=3,
                    ),
                )
                self.log_action(ActionRecord(actor_index, ActionType.DEFEND, ActionTarget.SELF, f"Raised {action.element.name} shield"))
            case ActionType.CAST_SPELL:
                spell_type = result.get("spell_type")
                match spell_type:
                    case SpellType.DAMAGE:
                        damage = self._calculate_damage(actor_state, defender_state, action, int(result["value"]))
                        self._apply_damage(defender_state, damage)
                        final_action_value = damage
                        self.log_action(ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.ENEMY, f"Dealt {damage}"))
                    case SpellType.BUFF:
                        self._apply_status(
                            actor_state,
                            StatusEffect(
                                name=action.name,
                                effect_type=StatusEffectType.BUFF,
                                value=float(result["value"]),
                                remaining_turns=4,
                            ),
                        )
                        self.log_action(ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.SELF, f"Buff {action.name}"))
                    case SpellType.DEBUFF:
                        self._apply_status(
                            defender_state,
                            StatusEffect(
                                name=action.name,
                                effect_type=StatusEffectType.DEBUFF,
                                value=float(result["value"]),
                                remaining_turns=3,
                            ),
                        )
                        self.log_action(ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.ENEMY, f"Debuff {action.name}"))

        self._decay_effects(actor_index)

        return action.success_announcement(actor_state.player.wizard, final_action_value)

    def get_winner(self) -> Optional[Wizard]:
        if self.player_states[0].current_health <= 0:
            return self.player_states[1].player.wizard
        if self.player_states[1].current_health <= 0:
            return self.player_states[0].player.wizard
        return None

    def _decay_effects(self, actor_index: int) -> None:
        actor_state = self.player_states[actor_index]
        defender_state = self.player_states[1 - actor_index]

        self._decrement_effects(actor_state, EffectGroup.BUFFS_AND_DEBUFFS)
        self._decrement_effects(defender_state, EffectGroup.DEFENSES)

    def _decrement_effects(self, state: PlayerState, group: EffectGroup) -> None:
        updated: List[StatusEffect] = []
        for effect in state.active_effects:
            if group.includes(effect):
                effect.remaining_turns = max(0, effect.remaining_turns - 1)
            if effect.remaining_turns > 0:
                updated.append(effect)
        state.active_effects = updated

    def _apply_heal(self, actor_state: PlayerState, amount: int) -> int:
        new_health = min(actor_state.max_health, actor_state.current_health + amount)
        healed = new_health - actor_state.current_health
        actor_state.current_health = new_health
        return healed

    def _apply_status(self, state: PlayerState, effect: StatusEffect) -> None:
        for existing in state.active_effects:
            if existing.name == effect.name:
                existing.remaining_turns = effect.remaining_turns
                existing.value = effect.value
                return
        state.active_effects.append(effect)

    def _calculate_damage(self, actor: PlayerState, defender: PlayerState, spell, base_damage: int) -> int:
        actor_multiplier = actor.player.wizard.damage_multiplier()
        for buff in actor.buffs():
            actor_multiplier *= (1 + buff.value)
        for debuff in actor.debuffs():
            actor_multiplier *= max(0.0, 1 - debuff.value)

        defender_multiplier = defender.player.wizard.damage_reduction()
        for buff in defender.buffs():
            defender_multiplier *= (1 + buff.value)
        for debuff in defender.debuffs():
            defender_multiplier *= max(0.0, 1 - debuff.value)

        damage = base_damage * actor_multiplier * defender_multiplier

        for defense in defender.defenses():
            defense_element = defense.name
            if defense_element in spell.element.strengths:
                damage *= 1.05
            elif defense_element in spell.element.weaknesses:
                damage *= 0.5
            else:
                damage *= 0.9

        return max(0, int(round(damage)))

    def _apply_damage(self, defender_state: PlayerState, damage: int) -> None:
        defender_state.current_health = max(0, defender_state.current_health - damage)

    def increment_mana(self) -> None:
        for state in self.player_states:
            state.current_mana += state.player.wizard.mana_per_round()

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        if len(self.player_states) < 2:
            return "GameState: <uninitialized>"

        lines: List[str] = []
        for idx, state in enumerate(self.player_states, start=1):
            lines.append(f"Player {idx}: {state}")

        lines.append("Actions:")
        if not self.action_log:
            lines.append("  (none)")
        else:
            for idx, action_record in enumerate(self.action_log, start=1):
                actor_label = "Player 1" if action_record.actor_id == 0 else "Player 2"
                lines.append(
                    f"  {idx}. {actor_label} -> {action_record.type.name} ({action_record.target.name}) | {action_record.result}"
                )

        return "\n".join(lines)


# Expose a singleton-style instance that can be imported anywhere.
game_state = GameState()

__all__ = [
    "StatusEffectType",
    "StatusEffect",
    "PlayerState",
    "ActionRecord",
    "GameState",
    "game_state",
]

