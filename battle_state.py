import pygame

from ai import AI
from battle_animations import AnimateMenu
from core import Core


class BattleState(object):
  def __init__(self):
    self.animations = []

  def transition(self, keys):
    old_num_animations = len(self.animations)
    self.animations = [
      animation for animation in self.animations
      if not animation.is_done()
    ]
    if self.animations:
      return self.do_animations()
    (state, redraw) = self.handle_input(keys)
    return (state, redraw or (len(self.animations) != old_num_animations))

  def do_animations(self):
    for animation in self.animations:
      animation.step()
    return (self, True)

  def handle_input(self, keys):
    raise NotImplementedError

  def get_display(self):
    display = {'menu': self.get_menu()}
    for animation in self.animations:
      animation.update_display(display)
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
    self.animations.append(AnimateMenu([self.base_text()]))

  def base_text(self):
    return 'What will %s do?' % (self.battle.get_name(self.user_id),)

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
    result = [self.base_text()]
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
    self.animations.append(AnimateMenu([self.base_text()]))

  def base_text(self):
    user = self.battle.get_pokemon(self.choices[-1]['user_id'])
    move = self.choices[-1]['move']
    return "Target for %s's %s:" % (user.name, move.name)

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
    result = [self.base_text(), '']
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
    self.execute_step(Core.execute)

  def execute_step(self, executor):
    '''
    Executes an executor/callback method and resets the display and
    internal state to account for it.
    '''
    result = executor(self.battle, self.choices)
    self.animations.extend(result.get('animations', []))
    self.menu = result.get('menu', [])
    if self.menu:
      self.animations.append(AnimateMenu(self.menu))
    self.callback = result.get('callback')

  def handle_input(self, keys):
    if pygame.K_d in keys or not self.menu:
      if self.callback:
        self.execute_step(self.callback)
        return (self, True)
      else:
        return (NextResult(self.battle, self.choices), True)
    return (self, False)

  def get_menu(self):
    return self.menu


def NextResult(battle, choices):
  if choices:
    return ExecuteTurn(battle, choices)
  return ChooseMove(battle)