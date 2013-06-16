from random import randint

from battle_state import Initialize
from pokemon import Pokemon


class Battle(object):
  def __init__(self):
    self.initialize()

  def initialize(self):
    self.num_pcs = 2
    self.num_npcs = 2
    self.pokemon = {('pc', i): Pokemon.random_pokemon() for i in range(self.num_pcs)}
    self.pokemon.update({('npc', i): Pokemon.random_pokemon() for i in range(self.num_npcs)})
    self.state = Initialize(self)

  def all_pcs(self):
    return [self.pokemon[('pc', i)] for i in range(self.num_pcs)]

  def all_npcs(self):
    return [self.pokemon[('npc', i)] for i in range(self.num_npcs)]

  def get_display(self):
    return self.state.get_display()

  def get_name(self, index):
    pokemon = self.pokemon[tuple(index)]
    return '%s%s' % ('Enemy ' if index[0] == 'npc' else '', pokemon.name)

  def get_pokemon(self, index):
    return self.pokemon[tuple(index)]

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
    # Delete moves for a) the Pokemon and b) the Pokemon that targeted it,
    # and shift all other move indices.
    for index in sorted(choices.iterkeys()):
      choice = choices.pop(index)
      retargeted_choice = self.retarget_choice(choice, to_remove)
      shifted_index = self.shift_left(index, to_remove)
      if retargeted_choice and shifted_index:
        choices[shifted_index] = retargeted_choice

  def retarget_choice(self, choice, to_remove):
    if choice.get('target_id') == to_remove:
      (side, i) = to_remove
      num_targets = self.num_pcs if side == 'pc' else self.num_npcs
      if not num_targets:
        return None
      new_i = i + randint(-1, 0)
      choice['target_id'] = (side, min(max(new_i, 0), num_targets - 1))
      print 'Retargeting from %s to %s' % (to_remove, choice['target_id'])
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
