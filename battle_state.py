import pygame

from ai import AI
from core import Core


class BattleState(object):
  def __init__(self):
    self.animations = []

  def transition(self, keys):
    if any(not animation.is_done() for animation in self.animations):
      return self.do_animations()
    return self.handle_input(keys)

  def do_animations(self):
    for animation in self.animations:
      animation.step()
    return (self, True)

  def handle_input(self, keys):
    raise NotImplementedError

  def get_display(self):
    display = {'menu': self.get_menu()}
    for animation in self.animations:
      animation.set_display(display)
    return display


class Initialize(BattleState):
  '''
  Initial state. For now, immediately transitions to choosing a move.
  '''
  def __init__(self, battle):
    super(Initialize, self).__init__()
    self.battle = battle

  def handle_input(self, keys):
    return (ChooseMove(self.battle), True)

  def get_menu(self):
    return []


class ChooseMove(BattleState):
  '''
  Choose a move for the current user pokemon.
  '''
  def __init__(self, battle, choices=None):
    super(ChooseMove, self).__init__()
    self.battle = battle
    self.choices = choices or []
    self.user_id = ('pc', len(self.choices))
    self.move = 0

  def handle_input(self, keys):
    pokemon = self.battle.get_pokemon(self.user_id)
    if pygame.K_UP in keys and self.move > 0:
      self.move -= 1
      return (self, True)
    if pygame.K_DOWN in keys and self.move < len(pokemon.moves) - 1:
      self.move += 1
      return (self, True)
    if pygame.K_s in keys and self.choices:
      return (ChooseMove(self.battle, self.choices[:-1]), True)
    if pygame.K_d in keys:
      self.choices.append({
        'type': 'move',
        'user_id': self.user_id,
        'move': pokemon.moves[self.move],
      })
      target_ids = self.choices[-1]['move'].get_target_ids(self.battle, self.user_id)
      if len(target_ids) > 1:
        return (ChooseTarget(self.battle, self.choices, target_ids), True)
      if target_ids:
        self.choices[-1]['target_id'] = target_ids[0]
      return (NextChoice(self.battle, self.choices), True)
    return (self, False)

  def get_menu(self):
    pokemon = self.battle.get_pokemon(self.user_id)
    result = ['What will %s do?' % (pokemon.name,)]
    for (i, move) in enumerate(pokemon.moves):
      cursor = '>' if i == self.move else ' '
      result.append(cursor + move.name)
    return result


def NextChoice(battle, choices=None):
  choices = choices or []
  if len(choices) < battle.num_pcs:
    return ChooseMove(battle, choices)
  # Let the AI make choices, then reformat the choices and pass to executor.
  choices.extend(AI.make_random_choices(battle))
  choices = {choice.pop('user_id'): choice for choice in choices}
  return ExecuteTurn(battle, choices)


class ChooseTarget(BattleState):
  '''
  Choose a target for a single-target move.
  '''
  def __init__(self, battle, choices, target_ids):
    super(ChooseTarget, self).__init__()
    self.battle = battle
    self.choices = choices
    self.target_ids = target_ids
    self.target = 0

  def handle_input(self, keys):
    old_target = self.target
    if pygame.K_LEFT in keys:
      self.target = max(self.target - 1, 0)
    if pygame.K_RIGHT in keys:
      self.target = min(self.target + 1, len(self.target_ids) - 1)
    if pygame.K_s in keys:
      return (ChooseMove(self.battle, self.choices[:-1]), True)
    if pygame.K_d in keys:
      self.choices[-1]['target_id'] = self.target_ids[self.target]
      return (NextChoice(self.battle, self.choices), True)
    return (self, self.target != old_target)

  def get_menu(self):
    user = self.battle.get_pokemon(self.choices[-1]['user_id'])
    move = self.choices[-1]['move']
    result = ["Target for %s's %s:" % (user.name, move.name), '']
    for (i, target_id) in enumerate(self.target_ids):
      target = self.battle.get_pokemon(target_id)
      cursor = '>' if i == self.target else ' '
      result[-1] += cursor + target.name + (12 - len(target.name))*' '
    return result


class ExecuteTurn(BattleState):
  '''
  Execute a step of the battle after the user has made their choices.
  This generally involves making one move and computing the effect.
  '''
  def __init__(self, battle, choices):
    super(ExecuteTurn, self).__init__()
    self.battle = battle
    self.choices = choices
    (self.menu, self.callback) = Core.execute(self.battle, self.choices)

  def handle_input(self, keys):
    old_menu = self.menu
    if pygame.K_d in keys:
      if self.callback:
        (self.menu, self.callback) = self.callback(self.battle, self.choices)
        return (self, True)
      else:
        return (NextResult(self.battle, self.choices), True)
    return (self, self.menu != old_menu)

  def get_menu(self):
    return self.menu


def NextResult(battle, choices):
  if choices:
    return ExecuteTurn(battle, choices)
  return ChooseMove(battle)
