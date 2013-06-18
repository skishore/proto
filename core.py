from collections import defaultdict
from random import sample

from battle_animations import (
  FaintPokemon,
  FlashPokemon,
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
        assert(choice['type'] == 'move')
        return choice['move'].execute(battle, index, choice.get('target_id'))

  @staticmethod
  def execution_order(battle):
    '''
    Returns a list of Pokemon indices sorted by speed. Ties are broken randomly.
    '''
    speeds = defaultdict(list)
    for (index, pokemon) in battle.pokemon.iteritems():
      speeds[pokemon.spe].append(index)
    for (speed, indices) in speeds.iteritems():
      speeds[speed] = sample(indices, len(indices))
    return sum((
      speeds[speed] for speed in
      sorted(speeds.iterkeys(), reverse=True)
    ), [])


class Callbacks(object):
  '''
  This class defines a number of static methods that return battle updates.
  These updates are functions with the same signature as Core.execute.
  '''
  @staticmethod
  def do_damage(battle, target_id, damage, message=None):
    def update(battle, choices):
      target = battle.get_pokemon(target_id)
      target.cur_hp = max(target.cur_hp - damage, 0)
      result = {'animations': [FlashPokemon(target_id)]}
      if target.cur_hp:
        menu = ['%s took %s damage.' % (battle.get_name(target_id), damage)]
        if message:
          menu = [message, ''] + menu
        result['callback'] = Callbacks.chain({'menu': menu})
      else:
        result['callback'] = Callbacks.faint(battle, target_id, message)
      return result
    return update

  @staticmethod
  def faint(battle, index, message=None):
    def update(battle, choices):
      menu = ['%s fainted!' % (battle.get_name(index),)]
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
