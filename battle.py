import pygame

from ai import make_ai_choices
from moves import do_moves
from pokedex import random_pokemon


class Battle(object):
  def __init__(self):
    self.user_pokemon = [random_pokemon() for i in xrange(1)]
    self.enemy_pokemon = [random_pokemon() for i in xrange(2)]
    self.state = BattleStates.Initialize(self)

  def compute_turn_results(self, user_choices):
    '''
    Takes a list of choices, which are (which_move, which_target) pairs.
    Computes the list of results and returns them.
    '''
    enemy_choices = make_ai_choices(self)
    return do_moves(self, user_choices, enemy_choices)

  def transition(self, keys):
    '''
    Transition functions should return a (new_state, update) pair,
    where update is a boolean which is True if state changed.
    '''
    (self.state, result) = self.state.transition(keys)
    return result

  def get_menu(self):
    return self.state.get_menu()

  def get_pokemon(self, index):
    (side, i) = index
    assert(side in ('user', 'enemy'))
    return self.user_pokemon[i] if side == 'user' else self.enemy_pokemon[i]


class BattleStates(object):
  class Initialize(object):
    '''
    Initial state. For now, immediately transitions to choosing a move.
    '''
    def __init__(self, battle):
      self.battle = battle

    def transition(self, keys):
      return (BattleStates.ChooseMove(self.battle), True)

    def get_menu(self):
      return []

  class ChooseMove(object):
    '''
    Choose a move for the `index`th user pokemon.
    '''
    def __init__(self, battle, choices=None):
      self.battle = battle
      self.choices = choices or []
      self.which_poke = len(self.choices)
      self.which_move = 0

    def transition(self, keys):
      pokemon = self.battle.user_pokemon[self.which_poke]
      if pygame.K_UP in keys and self.which_move > 0:
        self.which_move -= 1
        return (self, True)
      if pygame.K_DOWN in keys and self.which_move < len(pokemon.moves) - 1:
        self.which_move += 1
        return (self, True)
      if pygame.K_s in keys and self.choices:
        return (BattleStates.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices.append({
          'type': 'move',
          'poke': self.which_poke,
          'move': self.which_move,
        })
        return (BattleStates.ChooseTarget(self.battle, self.choices), True)
      return (self, False)

    def get_menu(self):
      pokemon = self.battle.user_pokemon[self.which_poke]
      result = ['What will %s do?' % (pokemon.name,)]
      for (i, move) in enumerate(pokemon.moves):
        cursor = '>' if i == self.which_move else ' '
        result.append(cursor + move['name'])
      return result

  class ChooseTarget(object):
    '''
    Choose a target for a single-target move.
    '''
    def __init__(self, battle, choices):
      self.battle = battle
      self.choices = choices
      self.which_enemy = 0

    def transition(self, keys):
      num_enemies = len(self.battle.enemy_pokemon)
      old_which_enemy = self.which_enemy
      if pygame.K_LEFT in keys:
        self.which_enemy = max(self.which_enemy - 1, 0)
      if pygame.K_RIGHT in keys:
        self.which_enemy = min(self.which_enemy + 1, num_enemies - 1)
      if pygame.K_s in keys:
        return (BattleStates.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices[-1]['target'] = self.which_enemy
        if len(self.choices) < len(self.battle.user_pokemon):
          return (BattleStates.ChooseMove(self.battle, self.choices), True)
        else:
          return (BattleStates.TurnResults(self.battle, self.choices), True)
      return (self, self.which_enemy != old_which_enemy)

    def get_menu(self):
      pokemon = self.battle.user_pokemon[self.choices[-1]['poke']]
      move = pokemon.moves[self.choices[-1]['move']]
      result = ["Target for %s's %s:" % (pokemon.name, move['name']), '']
      for (i, enemy) in enumerate(self.battle.enemy_pokemon):
        cursor = '>' if i == self.which_enemy else ' '
        result[-1] += cursor + enemy.name + (12 - len(enemy.name))*' '
      return result

  class TurnResults(object):
    '''
    Display the results of the battle.
    '''
    def __init__(self, battle, choices):
      self.battle = battle
      self.results = battle.compute_turn_results(choices)
      assert('menu' in self.results[0])
      self.which_result = 0

    def advance_result(self):
      if 'update' in self.results[self.which_result]:
        self.results[self.which_result]['update'](self.battle)
      self.which_result += 1

    def transition(self, keys):
      old_which_result = self.which_result
      if pygame.K_d in keys:
        self.advance_result()
        while self.which_result < len(self.results) and \
            'menu' not in self.results[self.which_result]:
          self.advance_result()
        if self.which_result == len(self.results):
          return (BattleStates.ChooseMove(self.battle), True)
      return (self, self.which_result == old_which_result)

    def get_menu(self):
      return self.results[self.which_result]['menu']
