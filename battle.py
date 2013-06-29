from random import randint

from battle_state import Initialize
from battle_ui import BattleUI
from pokemon import Pokemon


class Battle(object):
  def __init__(self):
    self.initialize()

  def initialize(self):
    self.sessions = 0
    self.num_pcs = 1
    self.num_npcs = 1
    self.pokemon = {}
    for index in [('pc', i) for i in range(self.num_pcs)]:
      self.add_pokemon(index, Pokemon.random_pokemon('pc'))
    for index in [('npc', i) for i in range(self.num_npcs)]:
      self.add_pokemon(index, Pokemon.random_pokemon('npc'))
    self.state = Initialize(self)
    self.soft_state = {}
    self.ui = BattleUI()

  def all_pcs(self):
    return [self.pokemon[('pc', i)] for i in range(self.num_pcs)]

  def all_npcs(self):
    return [self.pokemon[('npc', i)] for i in range(self.num_npcs)]

  def get_display(self):
    return self.state.get_display()

  def get_name(self, index, lower=False):
    pokemon = self.pokemon[tuple(index)]
    return '%s%s' % (
      ('enemy ' if lower else 'Enemy ') if index[0] == 'npc' else '',
      pokemon.name
    )

  def get_pokemon(self, index):
    return self.pokemon[tuple(index)]

  def add_pokemon(self, index, pokemon):
    pokemon.sess_id = self.sessions
    self.sessions += 1
    self.pokemon[index] = pokemon

  def remove_pokemon(self, to_remove, choices):
    '''
    Removes a Pokemon from this battle. Also modifies the choices dict:
      - Wipes out this Pokemon's choices from the dictionary so they are not executed.
      - Updates the indices of all other move users.
      - Updates the indices of moves' targets.

    If one side is now empty of Pokemon, then the game is over.
    '''
    # Remove the Pokemon from the side it's on.
    for index in sorted(self.pokemon.iterkeys()):
      pokemon = self.pokemon.pop(index)
      shifted_index = self.shift_left(index, to_remove)
      if shifted_index:
        self.pokemon[shifted_index] = pokemon
    # Update the count of pc/npcs.
    assert(to_remove[0] in ('pc', 'npc'))
    if to_remove[0] == 'pc':
      self.num_pcs -= 1
    else:
      self.num_npcs -= 1
    # Update the current choices and the last recorded choices dicts.
    self.update_choices(choices, to_remove)

  def update_choices(self, choices, to_remove):
    '''
    Modify the a choices dictionary to account for a removed Pokemon:
      - Delete moves that the Pokemon used from the dictionary.
      - Shift and retarget other moves in the dict.
    '''
    for index in sorted(choices.iterkeys()):
      choice = choices.pop(index)
      updated_choice = self.update_choice(choice, to_remove)
      shifted_index = self.shift_left(index, to_remove)
      if updated_choice and shifted_index:
        choices[shifted_index] = updated_choice

  def update_choice(self, choice, to_remove):
    if choice.get('target_id') == to_remove:
      (side, i) = to_remove
      num_targets = self.num_pcs if side == 'pc' else self.num_npcs
      if not num_targets:
        return None
      new_i = i + randint(-1, 0)
      choice['target_id'] = (side, min(max(new_i, 0), num_targets - 1))
    elif 'target_id' in choice:
      choice['target_id'] = self.shift_left(choice['target_id'], to_remove)
    return choice

  @staticmethod
  def shift_left(index, to_remove):
    if index[0] == to_remove[0] and index[1] >= to_remove[1]:
      if index[1] == to_remove[1]:
        return None
      return (index[0], index[1] - 1)
    return index

  def transition(self, keys):
    '''
    Transition functions should return a (new_state, update) pair,
    where update is a boolean which is True if state changed.
    '''
    (self.state, result) = self.state.transition(keys)
    return result

  def draw(self, screen):
    self.ui.draw(screen, self)
