#!/usr/bin/env python3

"""
Defines classes to be used throughout the game
"""

import random
import math
from enum import Enum, auto
from typing import List
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
    DAMAGE = (0.1)
    BUFF = (0.05)
    DEBUFF = (0.051)

    def __init__(self, variance: float):
        self.variance = variance


# ===============================================
#                Actual Classes
# ===============================================


class Action(ABC):
    """Represents a generic action a wizard can take on their turn"""

    def __init__(self, strength: float, accuracy: float, variance: float):
        self.strength = strength
        self.accuracy = accuracy
        self.variance = variance

    def succeeds_accuracy(self) -> bool:
        return random.random() <= self.accuracy

    def perform_action(self) -> dict:
        """
        Quick wrapper around subclass_action so we don't repeat the accuracy check code
        """
        if not self.succeeds_accuracy():
            return { "succeeded": False }

        return self.subclass_action()

    @abstractmethod
    def subclass_action(self) -> dict:
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


# ===============================================


class Heal(Action):
    """When the user elects to use their turn to restore HP"""
    ACCURACY = 0.95
    VARIANCE = 0.1

    def __init__(self, wizard):
        super().__init__(wizard.healing, Heal.ACCURACY, Heal.VARIANCE)

    def __str__(self) -> str:
        return (f"Action Type: {ActionType.HEAL}, "
                f"strength={self.strength:.2f}, "
                f"accuracy={self.accuracy:.2f}, "
                f"range={self.range()}, "
                f"mana cost={self.mana_cost()}")

    def _healing_base(self):
        return 150.0 * ((5.0 / 3.0) ** (self.strength ** 1.8))

    def subclass_action(self):
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

        min_val = healing_base * (1 - self.variance)
        max_val = healing_base * (1 + self.variance)
        return min_val, max_val

    def mana_cost(self) -> int:
        base = 2 * (4 ** (self.strength ** 1.15))
        return int(round(base))


# ===============================================


class Defend(Action):
    """When the user elects to defend for that turn"""
    ACCURACY = 1
    VARIANCE = 0

    def __init__(self, element: Element):
        super().__init__(1.0, Defend.ACCURACY, Defend.VARIANCE)
        self.element = element

    def __str__(self) -> str:
        return (f"Action Type: {ActionType.DEFEND}, "
                f"element={self.element.name}, "
                f"strength={self.strength:.2f}, "
                f"accuracy={self.accuracy:.2f}, "
                f"mana cost={self.mana_cost()}")

    def subclass_action(self):
        return {
            "succeeded": True,
            "value": self.element,
            "action_type": ActionType.DEFEND,
            "target": ActionTarget.SELF,
        }

    def range(self):
        pass

    def mana_cost(self) -> int:
        return 2
    

# ===============================================


class Spell(Action):
    """Represents a single spell"""

    def __init__(self, 
                name: str, 
                spell_type: SpellType, 
                description: str, 
                element: Element, 
                strength: float):
        super().__init__(strength, element.accuracy, spell_type.variance)
        self.name = name
        self.spell_type = spell_type
        self.description = description
        self.element = element

    def __str__(self) -> str:
        return (f"Action Type: {ActionType.CAST_SPELL}, "
                f"Spell name={self.name}, "
                f"Spell type={self.spell_type.name}, "
                f"element={self.element.name}, "
                f"strength={self.strength:.2f}, "
                f"accuracy={self.accuracy:.2f}, "
                f"description='{self.description}'), "
                f"range={self.range()}, "
                f"variance={self.variance}, "
                f"mana cost={self.mana_cost()}")

    def _spell_value(self) -> float:
        match self.spell_type:
            case SpellType.DAMAGE:
                return 100.0 * (2.0 ** (self.strength ** 2))
            case SpellType.BUFF:
                steps = int(self.strength / 0.2) + 1
                return steps * 0.05
            case SpellType.DEBUFF:
                steps = int(self.strength / 0.2) + 1
                return steps * 0.05

    def _target(self) -> ActionTarget:
        match self.spell_type:
            case SpellType.DAMAGE:
                return ActionTarget.ENEMY
            case SpellType.BUFF:
                return ActionTarget.SELF
            case SpellType.DEBUFF:
                return ActionTarget.ENEMY

    def subclass_action(self) -> dict:
        # Default values
        base = self._spell_value()
        target = self._target()
        variance = self.variance

        match self.spell_type:
            case SpellType.DAMAGE:
                value = int(round(_vary(base, variance)))
            case SpellType.BUFF:
                value = round(_vary(base, variance), 3)
            case SpellType.DEBUFF:
                value = round(_vary(base, variance), 3)

        return {
            "succeeded": True,
            "value": value,
            "action_type": ActionType.CAST_SPELL,
            "spell_type": self.spell_type,
            "target": target,
        }

    def range(self):
        """
        Returns the (min, max) possible values for this spell
        """
        variance = self.variance

        match self.spell_type:
            case SpellType.DAMAGE:
                base = 100.0 * (2.0 ** (self.strength ** 2))

            case SpellType.BUFF:
                steps = int(self.strength / 0.2) + 1
                base = steps * 0.05

            case SpellType.DEBUFF:
                steps = int(self.strength / 0.2) + 1
                base = steps * 0.05

        min_val = base * (1 - variance)
        max_val = base * (1 + variance)
        return min_val, max_val

    def mana_cost(self):
        """
        Calculate the mana cost of this spell.

        Formula:
          cost = 2 * (4 ^ (mana_cost ^ 1.15))
        Rounded to nearest integer.
        """
        base = 2 * (4 ** (self.strength ** 1.15))
        return int(round(base))



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
        return (f"Name: {self.name}\n "
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
                f"mpr={self.mana_per_round()}")


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
        Attack (0-1): dmg_mult = 0.75 * (5/3)^(attack^2), with ±10% variance.
        """
        base = 0.75 * ((5.0 / 3.0) ** (self.attack ** 2))
        varied = _vary(base)
        # Ensure it's positive
        return max(0.0, varied)

    def damage_reduction(self) -> float:
        """
        Defense (0-1): dmg_reduction = 0.9 * (14/9)^(defense^2), with ±10% variance.
        (Interpretation per given formula; engine can apply as designed.)
        """
        base = 0.9 * ((14.0 / 9.0) ** (self.defense ** 2))
        varied = _vary(base)
        return max(0.0, varied)

    def starting_mana(self) -> int:
        """
        Arcane (0-1): starting_mana = 5 * 2^(arcane^1.3), with ±10% variance.
        Returns an int >= 0.
        """
        base = 10.0 * (2.0 ** (self.arcane ** 1.3))
        varied = _vary(base)
        return max(0, int(round(varied)))

    def mana_per_round(self) -> int:
        """
        Calculate the amount of mana gained at the start of each round

        Formula:
          mana_gained = 2 * (4 ^ (arcane ^ 1.15))
        Rounded to nearest integer.
        """
        base = 2 * (4 ** (self.arcane ** 1.15))
        return int(round(base))

    # def all_actions(self) -> List[Action]:
    #     # Base 4 spells
    #     # Add in 1 heal
    #     # Add in 2 defenses


    # - Make healing at the wizard level again
    # - Add defending


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