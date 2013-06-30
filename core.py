from collections import defaultdict
from random import (
  randint,
  sample,
  uniform,
)

from battle_animations import (
  FaintPokemon,
  FlashPokemon,
)
from data import stat_names


class Core(object):
  @staticmethod
  def execute(battle, choices):
    '''
    Executes a move and returns a result dict, which may contain the following keys:
      - animations: a list of animations to run.
      - menu: a menu to display.
      - callback: a callback to execute after the menus are cleared.
    This method may update the battle and the set of remaining choices.
    '''
    assert(choices)
    for index in Core.execution_order(battle):
      if index in choices:
        choice = choices.pop(index)
        sess_id = battle.get_pokemon(index).sess_id
        result = Core.try_to_move(battle, index, choice)
        result['last_callback'] = Core.post_move_hook(sess_id)
        return result

  @staticmethod
  def execution_order(battle):
    '''
    Returns a list of Pokemon indices sorted by speed. Ties are broken randomly.
    '''
    speeds = defaultdict(list)
    for (index, pokemon) in battle.pokemon.iteritems():
      speeds[pokemon.stat('spe')].append(index)
    for (speed, indices) in speeds.iteritems():
      speeds[speed] = sample(indices, len(indices))
    return sum((
      speeds[speed] for speed in
      sorted(speeds.iterkeys(), reverse=True)
    ), [])

  @staticmethod
  def try_to_move(battle, index, choice):
    '''
    The Pokemon with the given index tries to move. If they are prevented from
    moving (for example, due to a status ailment), a message is shown instead.
    '''
    assert(choice['type'] == 'move')
    pokemon = battle.get_pokemon(index)
    (menu, can_move) = Status.transition(battle, index, pokemon)
    result = {'menu': menu}
    if can_move:
      move = choice['move'].execute(battle, index, choice.get('target_id'))
      if not menu:
        return move
      result['callback'] = lambda battle, choices: move
    return result

  @staticmethod
  def post_move_hook(sess_id):
    '''
    Get a callback to execute after this Pokemon moves, for example, burn damage.
    This callback will be executed even if the move's target faints.
    '''
    def update(battle, choices):
      for (index, pokemon) in battle.pokemon.iteritems():
        if pokemon.sess_id == sess_id:
          break
      else:
        return
      return Status.apply_update(battle, choices, index, pokemon)
    return update


class Callbacks(object):
  '''
  This class defines a number of static methods that return battle updates.
  These updates are functions with the same signature as Core.execute.
  '''
  max_buff = 6

  @staticmethod
  def do_damage(battle, target_id, damage, message, callback=None, special=''):
    def update(battle, choices):
      target = battle.get_pokemon(target_id)
      target.cur_hp = max(target.cur_hp - damage, 0)
      result = {'animations': [FlashPokemon(target_id)]}
      if target.cur_hp:
        menu = ['%s took %s damage%s.' % (battle.get_name(target_id), damage, special)]
        if message:
          menu = [message, ''] + menu
        result['callback'] = Callbacks.chain({'menu': menu, 'callback': callback})
      else:
        result['callback'] = Callbacks.faint(battle, target_id, message, special)
      return result
    return update

  @staticmethod
  def faint(battle, index, message, special=''):
    def update(battle, choices):
      menu = ['%s fainted%s!' % (battle.get_name(index), special)]
      if message:
        menu = [message, ''] + menu
      return {
        'menu': menu,
        'callback': lambda battle, choices: {
          'animations': [FaintPokemon(index, menu=menu)],
          'callback': (lambda battle, choices: battle.remove_pokemon(index, choices)),
        },
      }
    return update

  @staticmethod
  def chain(display, *rest):
    if rest:
      assert('callback' not in display)
      display['callback'] = Callbacks.chain(*rest)
    return lambda battle, choices: display

  @staticmethod
  def set_status(battle, target_id, status, callback=None):
    def update(battle, choices):
      menu = ['%s %s!' % (battle.get_name(target_id), Status.verbs[status])]
      def inner_update(battle, choices):
        Status.set_status(battle.get_pokemon(target_id), status)
        return {'callback': callback}
      return {'menu': menu, 'callback': inner_update}
    return update

  @staticmethod
  def do_buff(battle, target_id, stat, stages):
    def update(battle, choices):
      target = battle.get_pokemon(target_id)
      cur_stage = target.soft_status.get(stat, 0)
      new_stage = max(min(cur_stage + stages, Callbacks.max_buff), -Callbacks.max_buff)
      if new_stage != cur_stage:
        target.soft_status[stat] = new_stage
        return {'menu': ["%s's %s %s%s!" % (
          battle.get_name(target_id),
          stat_names[stat],
          'rose' if stages > 0 else 'fell',
          ' sharply' if abs(stages) > 1 else '',
        )]}
      return {'menu': ['But it failed!']}
    return update


class Status(object):
  letters = {
    'burn': 'B',
    'poison': 'P',
    'paralyze': 'R',
    'freeze': 'F',
    'sleep': 'S',
  }
  verbs = {
    'burn': 'was burned',
    'poison': 'was poisoned',
    'paralyze': 'was paralyzed',
    'freeze': 'was frozen solid',
    'sleep': 'fell asleep',
  }

  @staticmethod
  def apply_update(battle, choices, index, pokemon):
    if pokemon.status and hasattr(Status, 'apply_' + pokemon.status):
      callback = getattr(Status, 'apply_' + pokemon.status)(battle, index, pokemon)
      return callback(battle, choices)
    return None

  @staticmethod
  def apply_burn(battle, index, pokemon):
    damage = -(-pokemon.max_hp/8)
    special = ' from the burn'
    return Callbacks.do_damage(battle, index, damage, '', special=special)

  @staticmethod
  def apply_poison(battle, index, pokemon):
    damage = -(-pokemon.max_hp/8)
    special = ' from poison'
    return Callbacks.do_damage(battle, index, damage, '', special=special)

  @staticmethod
  def set_status(pokemon, status):
    pokemon.status = status
    if status == 'sleep':
      pokemon.soft_status['sleep_turns'] = randint(1, 7)

  @staticmethod
  def clear_status(pokemon):
    pokemon.status = None
    pokemon.soft_status.pop('sleep_turns', None)

  @staticmethod
  def transition(battle, index, pokemon):
    '''
    Transitions the status of a Pokemon with a status ailment. Returns a (menu, move)
    pair - the menu is a message to show, while move is True if the Pokemon can move.
    '''
    name = battle.get_name(index)
    if pokemon.status == 'sleep':
      pokemon.soft_status['sleep_turns'] -= 1
      if not pokemon.soft_status['sleep_turns']:
        Status.clear_status(pokemon)
        return (['%s woke up!' % (name,)], False)
      return (['%s was fast asleep!' % (name,)], False)
    elif pokemon.status == 'freeze':
      if uniform(0, 1) < 0.20:
        Status.clear_status(pokemon)
        return (['%s is frozen no more!' % (name,)], True)
      return (['%s is still frozen!' % (name,)], False)
    elif pokemon.status == 'paralyze':
      if uniform(0, 1) < 0.25:
        return (['%s is fully paralyzed!' % (name,)], False)
    return (None, True)
