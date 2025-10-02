import ActionType from "../enums/actionType";
import ActionTarget from "../enums/actionTarget";
import SpellType from "../enums/spellType";
import StatusEffectType from "../enums/statusEffectType";
import EffectGroup from "../enums/effectGroup";
import Player from "./player";
import PlayerState from "./playerState";
import StatusEffect from "./statusEffect";
import ActionRecord from "./actionRecord";

const shuffle = (array, randomFn = Math.random) => {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(randomFn() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
};

class GameState {
  constructor() {
    this.player_states = [];
    this.action_log = [];
  }

  initialize(wizard1, wizard2, randomFn = Math.random) {
    const assigned_order = shuffle([wizard1, wizard2], randomFn);
    this.player_states = assigned_order.map((wizard, index) => {
      const max_hp = wizard.max_hp(randomFn);
      return new PlayerState(
        new Player(index, wizard),
        max_hp,
        max_hp,
        wizard.starting_mana(randomFn),
        []
      );
    });

    this.action_log = [];
    return this.player_states.map((state) => state.player.wizard);
  }

  change_health(player, delta) {
    const state = this.player_states[player.id];
    state.current_health = Math.max(0, Math.min(state.max_health, state.current_health + delta));
    return state.current_health;
  }

  set_health(player, value) {
    const state = this.player_states[player.id];
    state.current_health = Math.max(0, Math.min(state.max_health, value));
    return state.current_health;
  }

  change_mana(player, delta) {
    const state = this.player_states[player.id];
    state.current_mana = Math.max(0, state.current_mana + delta);
    return state.current_mana;
  }

  set_mana(player, value) {
    const state = this.player_states[player.id];
    state.current_mana = Math.max(0, value);
    return state.current_mana;
  }

  add_status_effect(player, effect) {
    const state = this.player_states[player.id];
    const existing = state.active_effects.find((active) => active.name === effect.name);
    if (existing) {
      existing.remaining_turns = effect.remaining_turns;
      existing.value = effect.value;
      existing.effect_type = effect.effect_type;
      return;
    }
    state.active_effects.push(effect);
  }

  clear_expired_effects(player) {
    const state = this.player_states[player.id];
    state.active_effects = state.active_effects.filter((effect) => effect.remaining_turns > 0);
  }

  tick_effects() {
    this.player_states.forEach((state) => {
      state.active_effects.forEach((effect) => {
        effect.remaining_turns = Math.max(0, effect.remaining_turns - 1);
      });
    });
  }

  log_action(record) {
    this.action_log.push(record);
  }

  perform_action(actor_index, action, randomFn = Math.random) {
    if (actor_index !== 0 && actor_index !== 1) {
      throw new Error("actor_index must be 0 or 1");
    }

    const actor_state = this.player_states[actor_index];
    const defender_state = this.player_states[1 - actor_index];

    if (action.mana_cost() > actor_state.current_mana) {
      throw new Error("Not enough mana to perform action");
    }

    const result = action.perform_action(randomFn);

    if (!result?.succeeded) {
      this.log_action(new ActionRecord(actor_index, action.action_type, action.action_target(), "Failed :("));
      this._decay_effects(actor_index);
      return action.failure_announcement(actor_state.player.wizard);
    }

    actor_state.current_mana = Math.max(0, actor_state.current_mana - action.mana_cost());
    let final_action_value = result.value;

    switch (result.action_type) {
      case ActionType.HEAL: {
        const healed = this._apply_heal(actor_state, Number(result.value));
        final_action_value = healed;
        this.log_action(new ActionRecord(actor_index, ActionType.HEAL, ActionTarget.SELF, `Healed ${healed}`));
        break;
      }
      case ActionType.DEFEND: {
        this._apply_status(
          actor_state,
          new StatusEffect(
            action.element.name,
            StatusEffectType.DEFENSE,
            0.0,
            3
          )
        );
        this.log_action(new ActionRecord(actor_index, ActionType.DEFEND, ActionTarget.SELF, `Raised ${action.element.name} shield`));
        break;
      }
      case ActionType.CAST_SPELL: {
        switch (result.spell_type) {
          case SpellType.DAMAGE: {
            const damage = this._calculate_damage(actor_state, defender_state, action, Number(result.value));
            this._apply_damage(defender_state, damage);
            final_action_value = damage;
            this.log_action(new ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.ENEMY, `Dealt ${damage}`));
            break;
          }
          case SpellType.BUFF: {
            this._apply_status(
              actor_state,
              new StatusEffect(
                action.name,
                StatusEffectType.BUFF,
                Number(result.value),
                4
              )
            );
            this.log_action(new ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.SELF, `Buff ${action.name}`));
            break;
          }
          case SpellType.DEBUFF: {
            this._apply_status(
              defender_state,
              new StatusEffect(
                action.name,
                StatusEffectType.DEBUFF,
                Number(result.value),
                3
              )
            );
            this.log_action(new ActionRecord(actor_index, ActionType.CAST_SPELL, ActionTarget.ENEMY, `Debuff ${action.name}`));
            break;
          }
          default:
            throw new Error(`Unhandled spell type: ${result.spell_type}`);
        }
        break;
      }
      default:
        throw new Error(`Unhandled action type: ${result.action_type}`);
    }

    this._decay_effects(actor_index);

    return action.success_announcement(actor_state.player.wizard, final_action_value);
  }

  get_winner() {
    if (!this.player_states.length) {
      return null;
    }
    if (this.player_states[0].current_health <= 0) {
      return this.player_states[1].player.wizard;
    }
    if (this.player_states[1].current_health <= 0) {
      return this.player_states[0].player.wizard;
    }
    return null;
  }

  _decay_effects(actor_index) {
    const actor_state = this.player_states[actor_index];
    const defender_state = this.player_states[1 - actor_index];

    this._decrement_effects(actor_state, EffectGroup.BUFFS_AND_DEBUFFS);
    this._decrement_effects(defender_state, EffectGroup.DEFENSES);
  }

  _decrement_effects(state, group) {
    const updated = [];
    state.active_effects.forEach((effect) => {
      if (group.includes(effect)) {
        effect.remaining_turns = Math.max(0, effect.remaining_turns - 1);
      }
      if (effect.remaining_turns > 0) {
        updated.push(effect);
      }
    });
    state.active_effects = updated;
  }

  _apply_heal(state, amount) {
    const new_health = Math.min(state.max_health, state.current_health + amount);
    const healed = new_health - state.current_health;
    state.current_health = new_health;
    return healed;
  }

  _apply_status(state, effect) {
    const existing = state.active_effects.find((active) => active.name === effect.name);
    if (existing) {
      existing.remaining_turns = effect.remaining_turns;
      existing.value = effect.value;
      existing.effect_type = effect.effect_type;
      return;
    }
    state.active_effects.push(effect);
  }

  _calculate_damage(actor, defender, spell, base_damage) {
    let actor_multiplier = actor.player.wizard.damage_multiplier();
    actor.buffs().forEach((buff) => {
      actor_multiplier *= 1 + buff.value;
    });
    actor.debuffs().forEach((debuff) => {
      actor_multiplier *= Math.max(0, 1 - debuff.value);
    });

    let defender_multiplier = defender.player.wizard.damage_reduction();
    defender.buffs().forEach((buff) => {
      defender_multiplier *= 1 + buff.value;
    });
    defender.debuffs().forEach((debuff) => {
      defender_multiplier *= Math.max(0, 1 - debuff.value);
    });

    let damage = base_damage * actor_multiplier * defender_multiplier;

    defender.defenses().forEach((defense) => {
      const defense_element = defense.name;
      if (spell.element.strengths.includes(defense_element)) {
        damage *= 1.05;
      } else if (spell.element.weaknesses.includes(defense_element)) {
        damage *= 0.5;
      } else {
        damage *= 0.9;
      }
    });

    return Math.max(0, Math.round(damage));
  }

  _apply_damage(state, amount) {
    state.current_health = Math.max(0, state.current_health - amount);
  }

  increment_mana() {
    this.player_states.forEach((state) => {
      state.current_mana += state.player.wizard.mana_per_round();
    });
  }

  toString() {
    if (this.player_states.length < 2) {
      return "GameState: <uninitialized>";
    }

    const lines = this.player_states.map((state, idx) => `Player ${idx + 1}: ${state.toString()}`);
    lines.push("Actions:");
    if (!this.action_log.length) {
      lines.push("  (none)");
    } else {
      this.action_log.forEach((record, idx) => {
        const actor_label = record.actor_id === 0 ? "Player 1" : "Player 2";
        lines.push(`  ${idx + 1}. ${actor_label} -> ${record.type.name} (${record.target.name}) | ${record.result}`);
      });
    }

    return lines.join("\n");
  }
}

const game_state = new GameState();

export { GameState };
export default game_state;
