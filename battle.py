from collections import defaultdict
import pygame
from random import sample

from ai import make_ai_choices
from core import do_moves
from pokemon import Pokemon


class Battle(object):
  def __init__(self):
    self.num_pcs = 1
    self.num_npcs = 2
    self.pokemon = {('pc', i): Pokemon.random_pokemon() for i in range(self.num_pcs)}
    self.pokemon.update({('npc', i): Pokemon.random_pokemon() for i in range(self.num_npcs)})
    self.state = BattleStates.Initialize(self)

  def all_pcs(self):
    return [self.pokemon[('pc', i)] for i in range(self.num_pcs)]

  def all_npcs(self):
    return [self.pokemon[('npc', i)] for i in range(self.num_npcs)]

  def get_menu(self):
    return self.state.get_menu()

  def get_pokemon(self, index):
    return self.pokemon[tuple(index)]

  def compute_turn_results(self, choices):
    '''
    Takes a list of choices, which are (which_move, which_target) pairs.
    Computes the list of results and returns them.
    '''
    choices.extend(make_ai_choices(self))
    return do_moves(self, choices)

  def execution_order(self):
    '''
    Returns a list of Pokemon indices sorted by speed. Ties are broken randomly.
    '''
    speeds = defaultdict(list)
    for (index, pokemon) in self.pokemon.iteritems():
      speeds[pokemon.spe].append(index)
    for (speed, indices) in speeds.iteritems():
      speeds[speed] = sample(indices, len(indices))
    return sum((speeds[speed] for speed in sorted(speeds.iterkeys())), [])

  def transition(self, keys):
    '''
    Transition functions should return a (new_state, update) pair,
    where update is a boolean which is True if state changed.
    '''
    (self.state, result) = self.state.transition(keys)
    return result


class BattleStates(object):
  class Initialize(object):
    '''
    Initial state. For now, immediately transitions to choosing a move.
    '''
    def __init__(self, battle):
      self.battle = battle

    def transition(self, keys):
      return (BattleStates.NextMove(self.battle), True)

    def get_menu(self):
      return []

  class ChooseMove(object):
    '''
    Choose a move for the current user pokemon.
    '''
    def __init__(self, battle, choices=None):
      self.battle = battle
      self.choices = choices or []
      self.user = ('pc', len(self.choices))
      self.move = 0

    def transition(self, keys):
      pokemon = self.battle.get_pokemon(self.user)
      if pygame.K_UP in keys and self.move > 0:
        self.move -= 1
        return (self, True)
      if pygame.K_DOWN in keys and self.move < len(pokemon.moves) - 1:
        self.move += 1
        return (self, True)
      if pygame.K_s in keys and self.choices:
        return (BattleStates.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices.append({
          'type': 'move',
          'user': self.user,
          'move': pokemon.moves[self.move],
        })
        targets = self.choices[-1]['move'].get_targets(self.battle, self.user)
        if len(targets) > 1:
          return (BattleStates.ChooseTarget(self.battle, self.choices, targets), True)
        if targets:
          self.choices[-1]['target'] = targets[0]
        return (BattleStates.NextMove(self.battle, self.choices), True)
      return (self, False)

    def get_menu(self):
      pokemon = self.battle.get_pokemon(self.user)
      result = ['What will %s do?' % (pokemon.name,)]
      for (i, move) in enumerate(pokemon.moves):
        cursor = '>' if i == self.move else ' '
        result.append(cursor + move.name)
      return result

  @staticmethod
  def NextMove(battle, choices=None):
    choices = choices or []
    if len(choices) < battle.num_pcs:
      return BattleStates.ChooseMove(battle, choices)
    return BattleStates.TurnResults(battle, choices)

  class ChooseTarget(object):
    '''
    Choose a target for a single-target move.
    '''
    def __init__(self, battle, choices, targets):
      self.battle = battle
      self.choices = choices
      self.targets = targets
      self.target = 0

    def transition(self, keys):
      old_target = self.target
      if pygame.K_LEFT in keys:
        self.target = max(self.target - 1, 0)
      if pygame.K_RIGHT in keys:
        self.target = min(self.target + 1, len(self.targets) - 1)
      if pygame.K_s in keys:
        return (BattleStates.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices[-1]['target'] = self.targets[self.target]
        return (BattleStates.NextMove(self.battle, self.choices), True)
      return (self, self.target != old_target)

    def get_menu(self):
      user = self.battle.get_pokemon(self.choices[-1]['user'])
      move = self.choices[-1]['move']
      result = ["Target for %s's %s:" % (user.name, move.name), '']
      for (i, target) in enumerate(self.targets):
        target = self.battle.get_pokemon(target)
        cursor = '>' if i == self.target else ' '
        result[-1] += cursor + target.name + (12 - len(target.name))*' '
      return result

  class TurnResults(object):
    '''
    Display the results of the battle.
    '''
    def __init__(self, battle, choices):
      self.battle = battle
      self.results = battle.compute_turn_results(choices)
      assert('menu' in self.results[0])
      self.result = 0

    def advance_result(self):
      if 'update' in self.results[self.result]:
        self.results[self.result]['update'](self.battle)
      self.result += 1

    def transition(self, keys):
      old_result = self.result
      if pygame.K_d in keys:
        self.advance_result()
        while self.result < len(self.results) and \
            'menu' not in self.results[self.result]:
          self.advance_result()
        if self.result == len(self.results):
          return (BattleStates.ChooseMove(self.battle), True)
      return (self, self.result == old_result)

    def get_menu(self):
      return self.results[self.result]['menu']
