import pygame

from pokedex import random_pokemon


class Battle(object):
  def __init__(self):
    self.user_pokemon = [random_pokemon() for i in xrange(3)]
    self.enemy_pokemon = [random_pokemon() for i in xrange(7)]
    self.state = Battle.Initialize(self)

  def transition(self, keys):
    '''
    Transition functions should return a (new_state, update) pair,
    where update is a boolean which is True if state changed.
    '''
    (self.state, result) = self.state.transition(keys)
    return result

  def get_menu(self):
    return self.state.get_menu()

  class Initialize(object):
    '''
    Initial state. For now, immediately transitions to choosing a move.
    '''
    def __init__(self, battle):
      self.battle = battle

    def transition(self, keys):
      return (Battle.ChooseMove(self.battle), True)

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
        return (Battle.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices.append({
          'type': 'move',
          'poke': self.which_poke,
          'move': self.which_move,
        })
        return (Battle.ChooseTarget(self.battle, self.choices), True)
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
      half_num = (num_enemies + 1)/2 if num_enemies > 4 else num_enemies
      old_which_enemy = self.which_enemy
      if pygame.K_RIGHT in keys:
        if self.which_enemy not in (half_num - 1, num_enemies - 1):
          self.which_enemy += 1
      if pygame.K_LEFT in keys:
        if self.which_enemy not in (0, half_num):
          self.which_enemy -= 1
      if pygame.K_UP in keys:
        if self.which_enemy >= half_num:
          self.which_enemy = self.which_enemy - half_num
      if pygame.K_DOWN in keys:
        if self.which_enemy < half_num:
          self.which_enemy = min(self.which_enemy + half_num, num_enemies - 1)
      if pygame.K_s in keys:
        return (Battle.ChooseMove(self.battle, self.choices[:-1]), True)
      if pygame.K_d in keys:
        self.choices[-1]['target'] = self.which_enemy
        if len(self.choices) < len(self.battle.user_pokemon):
          return (Battle.ChooseMove(self.battle, self.choices), True)
      return (self, self.which_enemy != old_which_enemy)

    def get_menu(self):
      pokemon = self.battle.user_pokemon[self.choices[-1]['poke']]
      move = pokemon.moves[self.choices[-1]['move']]
      result = ["Target for %s's %s:" % (pokemon.name, move['name'])]

      num_enemies = len(self.battle.enemy_pokemon)
      half_num = (num_enemies + 1)/2 if num_enemies > 4 else num_enemies
      for (i, enemy) in enumerate(self.battle.enemy_pokemon):
        if i in (0, half_num):
          result.append('')
        cursor = '>' if i == self.which_enemy else ' '
        result[-1] += cursor + enemy.name + (12 - len(enemy.name))*' '
      return result
