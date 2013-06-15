from collections import defaultdict
from random import sample


class Core(object):
  @staticmethod
  def execute(battle, choices):
    '''
    Executes a single move and returns a (menus, callback) pair.
    The menus are displayed, and when they are emptied, the callback is called.

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
    return sum((speeds[speed] for speed in sorted(speeds.iterkeys())), [])


class Callbacks(object):
  '''
  This class defines a number of static methods that return battle updates.
  These updates are functions with the same signature as Core.execute.
  '''
  @staticmethod
  def do_damage(battle, target_id, damage):
    target = battle.get_pokemon(target_id)
    if damage < target.cur_hp:
      def update(battle, choices):
        target.cur_hp -= damage
        return ([['%s took %s damage.' % (battle.get_name(target_id), damage)]], None)
      return update
    else:
      return Callbacks.faint(battle, target_id)

  @staticmethod
  def faint(battle, index):
    def update(battle, choices):
      if index in choices:
        del choices[index]
      battle.get_pokemon(index).cur_hp = 0
      return ([['%s fainted!' % (battle.get_name(index),)]], None)
    return update
