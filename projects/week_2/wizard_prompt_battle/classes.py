#!/usr/bin/env python3

"""
Defines classes to be used throughout the game
"""

import random
import math
from enum import Enum, auto
from typing import Any, Dict, List
from abc import ABC, abstractmethod

# ===============================================
#                  Enums
# ===============================================

class Element(Enum):
    FIRE = (
        "Fire",
        "Represents destruction, passion, and energy.",
        ["ICE", "DEATH"],    # Strengths
        ["STORM", "MYTH"],   # Weaknesses
        0.75                 # accuracy
    )
    ICE = (
        "Ice",
        "Represents control, patience, and slow movements.",
        ["STORM", "MYTH"],
        ["FIRE", "LIFE"],
        0.8
    )
    STORM = (
        "Storm",
        "Represents chaos, unpredictability, and raw power.",
        ["FIRE", "LIFE"],
        ["ICE", "BALANCE"],
        0.7
    )
    LIFE = (
        "Life",
        "Represents healing, vitality, and growth.",
        ["DEATH", "MYTH"],
        ["STORM", "ICE"],
        0.9
    )
    DEATH = (
        "Death",
        "Represents decay, sacrifice, and inevitability.",
        ["LIFE", "BALANCE"],
        ["FIRE", "MYTH"],
        0.85
    )
    MYTH = (
        "Myth",
        "Represents illusions, trickery, and ancient power.",
        ["FIRE", "DEATH"],
        ["ICE", "LIFE"],
        0.8
    )
    BALANCE = (
        "Balance",
        "Represents harmony, control, and versatility.",
        ["STORM", "MYTH"],
        ["DEATH", "LIFE"],
        0.85
    )

    def __init__(self, display_name: str, description: str, strengths: List[str], weaknesses: List[str], accuracy: float):
        self._display_name = display_name
        self._description = description
        self._strengths = strengths
        self._weaknesses = weaknesses
        self._accuracy = accuracy

    @property
    def display_name(self):
        return self._display_name

    @property
    def description(self):
        return self._description

    @property
    def strengths(self):
        return self._strengths

    @property
    def weaknesses(self):
        return self._weaknesses

    @property
    def accuracy(self):
        return self._accuracy

class ActionType(Enum):
    CAST_SPELL = auto()
    HEAL = auto()
    DEFEND = auto()

class ActionTarget(Enum):
    SELF = auto()
    ENEMY = auto()

class SpellType(Enum):
    DAMAGE = auto()
    BUFF = auto()
    DEBUFF = auto()

    @property
    def variance(self) -> float:
        return {
            SpellType.DAMAGE: 0.1,
            SpellType.BUFF: 0.05,
            SpellType.DEBUFF: 0.05,
        }[self]


# ===============================================
#                Actual Classes
# ===============================================


class Action(ABC):
    """Represents a generic action a wizard can take on their turn"""

    def __init__(self, action_type: ActionType, strength: float, accuracy: float, variance: float):
        self.action_type = action_type
        self.strength = strength
        self.accuracy = accuracy
        self.variance = variance

    def succeeds_accuracy(self) -> bool:
        return random.random() <= self.accuracy

    def perform_action(self) -> dict:
        """
        Quick wrapper around perform_action_subclass so we don't repeat the accuracy check code
        """
        if not self.succeeds_accuracy():
            return { "succeeded": False }

        return self.perform_action_subclass()

    @abstractmethod
    def perform_action_subclass(self) -> dict:
        """
        Subclasses must define what happens when you perform this action
        """
        pass

    @abstractmethod
    def range(self):
        """
        Returns the (min, max) possible values for this action (if applicable)
        """
        pass

    @abstractmethod
    def mana_cost(self) -> int:
        """
        How much mana it costs to perform this action
        """
        pass

    @abstractmethod
    def overview(self) -> str:
        """
        A brief overview describing what this action does (for LLM)
        """
        pass

    @abstractmethod
    def failure_announcement(self, wizard) -> str:
        """
        A brief announcement describing what happens when this action fails (for the players to see)
        """
        pass

    @abstractmethod
    def success_announcement(self, wizard, value: float) -> str:
        """
        A brief announcement describing what happens when this action succeeds (for the players to see)
        """
        pass

    @abstractmethod
    def action_target(self) -> ActionTarget:
        """
        Returns the target of this action
        """
        pass

    @abstractmethod
    def display_card(self) -> Dict[str, Any]:
        """
        Returns a JSON-serialisable payload describing this action for UI cards.
        """
        pass


# ===============================================


class Heal(Action):
    """When the user elects to use their turn to restore HP"""
    ACCURACY = 0.95
    VARIANCE = 0.1

    def __init__(self, wizard):
        super().__init__(ActionType.HEAL, wizard.healing, Heal.ACCURACY, Heal.VARIANCE)

    def __str__(self) -> str:
        lines = [
            "Heal Action:",
            f"  action_type: {ActionType.HEAL.name}",
            f"  strength: {self.strength:.2f}",
            f"  accuracy: {self.accuracy:.2f}",
            f"  range: {self.range()}",
            f"  mana_cost: {self.mana_cost()}",
        ]
        return "\n".join(lines)

    def _healing_base(self):
        return 150.0 * ((5.0 / 3.0) ** (self.strength ** 1.8))

    def perform_action_subclass(self):
        healing_base = self._healing_base()
        healing_amount = max(0, int(round(_vary(healing_base, self.variance))))

        return {
            "succeeded": True,
            "value": healing_amount,
            "action_type": ActionType.HEAL,
            "target": ActionTarget.SELF,
        }

    def range(self):
        healing_base = self._healing_base()

        min_val = int(round(healing_base * (1 - self.variance)))
        max_val = int(round(healing_base * (1 + self.variance)))
        return min_val, max_val

    def mana_cost(self) -> int:
        base = 3 * (2 ** (self.strength ** 1.15))
        return int(round(base))

    def overview(self) -> str:
        parts = [
            "Action Type: 'HEAL'",
            f"Accuracy: {100 * self.accuracy}%",
            f"Target: {ActionTarget.SELF.name}",
            f"Mana Cost: {self.mana_cost()}",
            f"Description: Restores {self.range()[0]} to {self.range()[1]} hp",
        ]
        return ", ".join(parts)

    def failure_announcement(self, wizard) -> str:
        return f"{wizard.name} casts heal... but it failed!"

    def success_announcement(self, wizard, value: float) -> str:
        return f"{wizard.name}  casts heal. {int(value)} health was restored!"

    def action_target(self) -> ActionTarget:
        return ActionTarget.SELF

    def display_card(self) -> Dict[str, Any]:
        min_val, max_val = self.range()
        return {
            "type": "HEAL",
            "element": None,
            "name": "Heal",
            "description": f"Restores {min_val}-{max_val} health.",
            "accuracy": self.accuracy,
            "mana_cost": self.mana_cost(),
        }


# ===============================================


class Defend(Action):
    """When the user elects to defend for that turn"""
    ACCURACY = 1.0
    VARIANCE = 0.0

    def __init__(self, element: Element):
        super().__init__(ActionType.DEFEND, 1.0, Defend.ACCURACY, Defend.VARIANCE)
        self.element = element

    def __str__(self) -> str:
        lines = [
            "Defend Action:",
            f"  action_type: {ActionType.DEFEND.name}",
            f"  element: {self.element.name}",
            f"  strength: {self.strength:.2f}",
            f"  accuracy: {self.accuracy:.2f}",
            f"  mana_cost: {self.mana_cost()}",
        ]
        return "\n".join(lines)

    def perform_action_subclass(self):
        return {
            "succeeded": True,
            "value": self.element,
            "action_type": ActionType.DEFEND,
            "target": ActionTarget.SELF,
        }

    def range(self):
        pass

    def mana_cost(self) -> int:
        return 0

    def overview(self) -> str:
        parts = [
            "Action Type: 'DEFEND'",
            f"Element: {self.element.name}",
            f"Accuracy: {100 * self.accuracy}%",
            f"Target: {ActionTarget.SELF.name}",
            f"Mana Cost: {self.mana_cost()}",
            f"Description: Puts up a {self.element.name} shield to greatly reduce incoming damage",
            f"Elements strong against: {', '.join(self.element.strengths)}",
            f"Elements weak against: {', '.join(self.element.weaknesses)}",
        ]
        return ", ".join(parts)

    def failure_announcement(self, wizard) -> str:
        return f"{wizard.name} failed a defense? How?!?!?"

    def success_announcement(self, wizard, value: float) -> str:
        return f"{wizard.name} put up a {self.element.name} shield!"

    def action_target(self) -> ActionTarget:
        return ActionTarget.SELF
    
    def display_card(self) -> Dict[str, Any]:
        strengths = ", ".join(self.element.strengths)
        weaknesses = ", ".join(self.element.weaknesses)
        description = (
            f"Raises a {self.element.display_name} shield. "
            f"Strong vs {strengths}. Weak vs {weaknesses}."
        )
        return {
            "type": "DEFENSE",
            "element": self.element.name,
            "name": f"{self.element.display_name} Defense",
            "description": description,
            "accuracy": self.accuracy,
            "mana_cost": self.mana_cost(),
        }


# ===============================================


class Spell(Action):
    """Represents a single spell"""

    def __init__(self, 
                name: str, 
                spell_type: SpellType, 
                description: str, 
                element: Element, 
                strength: float):
        super().__init__(ActionType.CAST_SPELL, strength, element.accuracy, spell_type.variance)
        self.name = name
        self.spell_type = spell_type
        self.description = description
        self.element = element

    def __str__(self) -> str:
        lines = [
            "Spell Action:",
            f"  action_type: {ActionType.CAST_SPELL.name}",
            f"  name: {self.name}",
            f"  spell_type: {self.spell_type.name}",
            f"  element: {self.element.name}",
            f"  strength: {self.strength:.2f}",
            f"  accuracy: {self.accuracy:.2f}",
            f"  variance: {self.variance:.3f}",
            f"  range: {self.range()}",
            f"  mana_cost: {self.mana_cost()}",
            f"  description: {self.description}",
        ]
        return "\n".join(lines)

    def _base_spell_value(self) -> float:
        match self.spell_type:
            case SpellType.DAMAGE:
                return 100.0 * (2.0 ** (self.strength ** 2))
            case SpellType.BUFF:
                return 0.1 * ((0.25 / 0.1) ** (self.strength ** 1.8))
            case SpellType.DEBUFF:
                return 0.1 * ((0.25 / 0.1) ** (self.strength ** 1.8))

    def _varied_spell_value(self) -> float:
        base_value = self._base_spell_value()
        varied_spell_value = _vary(base_value, self.variance)
        return self._round_spell_value(varied_spell_value)

    def _round_spell_value(self, value: float) -> float:
        match self.spell_type:
            case SpellType.DAMAGE:
                return int(round(value))
            case SpellType.BUFF:
                return round(value, 3)
            case SpellType.DEBUFF:
                return round(value, 3)

    def action_target(self) -> ActionTarget:
        match self.spell_type:
            case SpellType.DAMAGE:
                return ActionTarget.ENEMY
            case SpellType.BUFF:
                return ActionTarget.SELF
            case SpellType.DEBUFF:
                return ActionTarget.ENEMY

    def _spell_effect(self) -> str:
        match self.spell_type:
            case SpellType.DAMAGE:
                return f"Deals {self.range()[0]}-{self.range()[1]} damage"
            case SpellType.BUFF:
                return f"Increases your attack and defense by {self.range()[0]}-{self.range()[1]}% for 3 rounds"
            case SpellType.DEBUFF:
                return f"Reduces enemy attack and defense by {self.range()[0]}-{self.range()[1]}% for 3 rounds"

    def perform_action_subclass(self) -> dict:
        # Default values
        spell_value = self._varied_spell_value()
        target = self.action_target()

        return {
            "succeeded": True,
            "value": spell_value,
            "action_type": ActionType.CAST_SPELL,
            "spell_type": self.spell_type,
            "target": target,
        }

    def range(self):
        """
        Returns the (min, max) possible values for this spell
        """
        base = self._base_spell_value()
        variance = self.variance

        min_val = self._round_spell_value(base * (1 - variance))
        max_val = self._round_spell_value(base * (1 + variance))

        return min_val, max_val

    def mana_cost(self):
        """
        Calculate the mana cost of this spell.

        Formula:
          cost = 2 * (4 ^ (mana_cost ^ 1.15))
        Rounded to nearest integer.
        """
        base = 3 * ((10.0 / 3.0) ** (self.strength ** 1.15))
        return int(round(base))

    def overview(self) -> str:
        parts = [
            "Action Type: 'CAST_SPELL'",
            f"Spell Type: {self.spell_type.name}",
            f"Element: {self.element.name}",
            f"Accuracy: {100 * self.accuracy}%",
            f"Target: {self.action_target().name}",
            f"Mana Cost: {self.mana_cost()}",
            f"Description: {self._spell_effect()}",
            f"Elements strong against: {', '.join(self.element.strengths)}",
            f"Elements weak against: {', '.join(self.element.weaknesses)}",
        ]
        return ", ".join(parts)

    def failure_announcement(self, wizard) -> str:
        return f"{wizard.name} casts {self.name}... but it failed!"

    def success_announcement(self, wizard, value: float) -> str:
        match self.spell_type:
            case SpellType.DAMAGE:
                return f"{wizard.name} casts {self.name} dealing {int(value)} damage!"
            case SpellType.BUFF:
                return f"{wizard.name} casts {self.name}. Their attack and defense increase by {value}%!"
            case SpellType.DEBUFF:
                return f"{wizard.name} casts {self.name}. Their opponent's attack and defense decrease by {value}%!"

    def display_card(self) -> Dict[str, Any]:
        return {
            "type": self.spell_type.name,
            "element": self.element.name,
            "name": self.name,
            "description": self._spell_effect(),
            "accuracy": self.accuracy,
            "mana_cost": self.mana_cost(),
        }

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
    @staticmethod
    def build_from_json(data: Dict[str, Any]) -> "Spell":
        required = ["name", "spell_type", "description", "element", "strength"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing keys for Spell: {', '.join(missing)}")

        return Spell(
            name=str(data["name"]),
            spell_type=SpellType[str(data["spell_type"]).upper()],
            description=str(data["description"]),
            element=Element[str(data["element"]).upper()],
            strength=float(data["strength"]),
        )



# ===============================================


class Wizard:
    """Represents a particular wizard"""

    def __init__(self, 
                name: str, 
                primary_element: Element,
                secondary_element: Element, 
                attack: float, 
                defense: float, 
                health: float, 
                healing: float,
                arcane: float,
                spells: List[Spell],
                combat_style: str):
        self.name = name
        self.primary_element = primary_element
        self.secondary_element = secondary_element
        self.attack = attack
        self.defense = defense
        self.health = health
        self.healing = healing
        self.arcane = arcane
        self.spells = spells
        self.combat_style = combat_style

    def __str__(self) -> str:
        header = (
            f"Name: {self.name}\n "
            f"Primary element={self.primary_element}\n "
            f"Secondary element={self.secondary_element}\n "
            f"attack={self.attack}\n "
            f"defense={self.defense}\n "
            f"health={self.health}\n "
            f"healing={self.healing}\n "
            f"arcane={self.arcane}\n "
            f"combat style={self.combat_style}\n "
            f"max hp={self.max_hp()}\n "
            f"damage mult={self.damage_multiplier()}\n "
            f"damage red={self.damage_reduction()}\n "
            f"starting mana={self.starting_mana()}\n "
            f"mpr={self.mana_per_round()}\n"
        )

        actions = [action.overview() for action in self.all_actions()]
        actions_block = "\n ".join(f"Action {idx+1}: {desc}" for idx, desc in enumerate(actions))

        return f"{header} Available actions:\n {actions_block}"


    def max_hp(self) -> int:
        """
        Health (0-1): hp = 500 * 2^(health^2), with ±10% variance.
        Returns an int >= 1.
        """
        base = 500.0 * (2.0 ** (self.health ** 2))
        varied = _vary(base)
        return max(1, int(round(varied)))

    def damage_multiplier(self) -> float:
        """
        Attack (0-1): dmg_mult = (1.25)^(attack^2)
        """
        return (1.25 ** (self.attack ** 2))

    def damage_reduction(self) -> float:
        """
        Defense (0-1): dmg_reduction = 1.1 * (8/11)^(defense^1.8)
        """
        return 1.1 * ((8.0 / 11.0) ** (self.defense ** 1.8))

    def starting_mana(self) -> int:
        """
        Arcane (0-1): starting_mana = 10 * 2^(arcane^1.3), with ±10% variance.
        Returns an int >= 0.
        """
        base = 10.0 * (2.0 ** (self.arcane ** 1.3))
        varied = _vary(base)
        return max(0, int(round(varied)))

    def mana_per_round(self) -> int:
        """
        Calculate the amount of mana gained at the start of each round

        Formula:
          mana_gained = 2 * (3 ^ (arcane ^ 1.15))
        Rounded to nearest integer.
        """
        base = 2 * ((2.5) ** (self.arcane ** 1.15))
        return int(round(base))

    def all_actions(self) -> List[Action]:
        spell_priority = {
            SpellType.DAMAGE: 0,
            SpellType.BUFF: 1,
            SpellType.DEBUFF: 2,
        }

        sorted_spells = sorted(
            self.spells,
            key=lambda spell: (
                spell_priority.get(spell.spell_type, float("inf")),
                spell.name.lower(),
            ),
        )

        actions: List[Action] = []
        actions.extend(sorted_spells)
        actions.append(Heal(self))
        actions.append(Defend(self.primary_element))
        actions.append(Defend(self.secondary_element))

        return actions

    def affordable_actions(self, mana_cap: int) -> List[Action]:
        return [action for action in self.all_actions() if action.mana_cost() <= mana_cap]

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
    @staticmethod
    def build_from_json(data: Dict[str, Any]) -> "Wizard":
        required = [
            "name",
            "primary_element",
            "secondary_element",
            "attack",
            "defense",
            "health",
            "healing",
            "arcane",
            "combat_style",
            "spells",
        ]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing keys for Wizard: {', '.join(missing)}")

        spells_payload = data["spells"]
        if not isinstance(spells_payload, list):
            raise ValueError("Wizard 'spells' must be a list")

        spells = [Spell.build_from_json(spell) for spell in spells_payload]

        return Wizard(
            name=str(data["name"]),
            primary_element=Element[str(data["primary_element"]).upper()],
            secondary_element=Element[str(data["secondary_element"]).upper()],
            attack=float(data["attack"]),
            defense=float(data["defense"]),
            health=float(data["health"]),
            healing=float(data["healing"]),
            arcane=float(data["arcane"]),
            spells=spells,
            combat_style=str(data["combat_style"]),
        )


# ===============================================


class EnemyWizard(Wizard):
    """A wizard that you have to face off against"""

    def __init__(self, 
                name: str, 
                primary_element: Element,
                secondary_element: Element, 
                attack: float, 
                defense: float, 
                health: float, 
                healing: float,
                arcane: float,
                spells: List[Spell],
                combat_style: str,
                preview: str):
        super().__init__(name, primary_element, secondary_element, attack, defense, health, healing, arcane, spells, combat_style)
        self.preview = preview


# ===============================================
#               Helper Methods
# ===============================================

def _vary(value: float, pct: float = 0.10) -> float:
    """
    Apply a random ±pct variance to value.
    Example: pct=0.10 -> uniform in [0.9, 1.1].
    """
    factor = random.uniform(1.0 - pct, 1.0 + pct)
    return value * factor