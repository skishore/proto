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
from data import (
  Stat,
  Status,
  Type,
)


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
      speeds[pokemon.stat(Stat.SPEED)].append(index)
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
    (menu, can_move) = StatusEffects.transition(battle, index, pokemon)
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
      return StatusEffects.apply_update(battle, choices, index, pokemon)
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
  def set_status(battle, target_id, status, source, callback=None, noisy_failure=False):
    def update(battle, choices):
      if StatusEffects.set_status(battle, target_id, status, choices, source=source):
        menu = ['%s %s!' % (battle.get_name(target_id), Status.VERBS[status])]
        return {'menu': menu, 'callback': callback}
      elif noisy_failure:
        return {'menu': ['But it failed!'], 'callback': callback}
      elif callback:
        return callback(battle, choices)
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
          stat,
          'rose' if stages > 0 else 'fell',
          ' sharply' if abs(stages) > 1 else '',
        )]}
      return {'menu': ['But it failed!']}
    return update


class StatusEffects(object):
  @staticmethod
  def set_status(battle, target_id, status, choices, source):
    '''
    Sets a Pokemon's status. Returns True if it is set.
    '''
    pokemon = battle.get_pokemon(target_id)
    if status in Status.SOFT_STATUSES:
      assert(status == Status.FLINCH), 'Soft status %s is not implemented' % (status,)
      if target_id in choices and pokemon.status not in (Status.SLEEP, Status.FREEZE):
        del choices[target_id]
        return True
      return False
    elif not pokemon.status:
      assert(status in Status.OPTIONS), 'Unexpected status: %s' % (status,)
      if not StatusEffects.check_immunity(pokemon, status, source.type):
        pokemon.status = status
        if status == Status.SLEEP:
          pokemon.soft_status['sleep_turns'] = randint(1, 7)
        return True

  @staticmethod
  def check_immunity(pokemon, status, source_type):
    if status == Status.BURN:
      return Type.FIRE in pokemon.types
    if status == Status.FREEZE:
      return Type.ICE in pokemon.types and source_type == Type.ICE
    if status == Status.POISON:
      return (
        (Type.POISON in pokemon.types or Type.STEEL in pokemon.types) and
        source_type == Type.POISON
      )

  @staticmethod
  def clear_status(pokemon):
    pokemon.status = None
    pokemon.soft_status.pop('sleep_turns', None)

  @staticmethod
  def apply_update(battle, choices, index, pokemon):
    if pokemon.status and hasattr(StatusEffects, 'apply_' + pokemon.status):
      callback = getattr(StatusEffects, 'apply_' + pokemon.status)(battle, index, pokemon)
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
  def transition(battle, index, pokemon):
    '''
    Transitions the status of a Pokemon with a status ailment. Returns a (menu, move)
    pair - the menu is a message to show, while move is True if the Pokemon can move.
    '''
    name = battle.get_name(index)
    if pokemon.status == Status.SLEEP:
      pokemon.soft_status['sleep_turns'] -= 1
      if not pokemon.soft_status['sleep_turns']:
        StatusEffects.clear_status(pokemon)
        return (['%s woke up!' % (name,)], False)
      return (['%s was fast asleep!' % (name,)], False)
    elif pokemon.status == Status.FREEZE:
      if uniform(0, 1) < 0.20:
        StatusEffects.clear_status(pokemon)
        return (['%s is frozen no more!' % (name,)], False)
      return (['%s is still frozen!' % (name,)], False)
    elif pokemon.status == Status.PARALYZE:
      if uniform(0, 1) < 0.25:
        return (['%s is fully paralyzed!' % (name,)], False)
    return (None, True)
