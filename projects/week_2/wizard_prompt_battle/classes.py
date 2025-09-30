#!/usr/bin/env python3

"""
Defines classes to be used throughout the game
"""

from enum import Enum, auto
from typing import List

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


class SpellType(Enum):
    DAMAGE = auto()
    BUFF = auto()
    DEBUFF = auto()



# ===============================================
#                Actual Classes
# ===============================================

class Spell:
    """Represents a single spell"""

    def __init__(self, 
                name: str, 
                spell_type: SpellType, 
                description: str, 
                element: Element, 
                strength: float, 
                mana_cost: int):
        self.name = name
        self.spell_type = spell_type
        self.description = description
        self.element = element
        self.strength = strength
        self.mana_cost = mana_cost
        self.accuracy = element.accuracy

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


# Each wizard has:
# - Name
# - Primary Element
# - Secondary Element
# - Attack (0-1, damage_multiplier = 0.75 * (5/3)^attack^2)
# - Defense (0-1, damage_reduction = 0.9 * (14/9)^defense^2)
# - Health (0-1, hp = 500 * 2^health^2)
# - Healing (0-1, health_restoration = 150 * (5/3)^healing^1.8)
# - Arcane (0-1)
#   - starting_mana = 5 * 2^arcane^1.3
#   - mana_per_round = 2 if 0-0.6, 3 if 0.61-0.85, 4 if > 0.85
# - Spells (damage, debuff, buff)
# - Combat style (blurb)

# Spell composition:
# - Literally whatever, that's part of the fun