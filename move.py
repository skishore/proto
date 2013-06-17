import operator
from random import (
  sample,
  uniform,
  )

from core import Callbacks
from data import (
  move_data,
  type_effectiveness,
  )


class Move(object):
  attrs = ('name', 'accuracy', 'power', 'type')
  moves = move_data.keys()

  def __init__(self, num):
    self.num = num
    data = move_data[num]
    for attr in self.attrs:
      setattr(self, attr, data[attr])
    self.max_pp = data['pp']
    self.cur_pp = self.max_pp

  def get_target_ids(self, battle, index):
    # A placeholder implementation of a damaging, single-target move.
    # Some moves might target user pokemon, or have no target at all.
    if index[0] == 'npc':
      return [('pc', i) for i in range(battle.num_pcs)]
    return [('npc', i) for i in range(battle.num_npcs)]

  def execute(self, battle, user_id, target_id):
    '''
    Move execution methods should return a (menus, callback) pair.
    '''
    # A placeholder implementation of a damaging, single-target move.
    user = battle.get_pokemon(user_id)
    target = battle.get_pokemon(target_id)
    menu = ['%s used %s!' % (battle.get_name(user_id), self.name)]
    damage = self.compute_damage(battle, user, target)
    callback = Callbacks.do_damage(battle, target_id, damage)
    return {'menu': menu, 'callback': callback}

  def compute_damage(self, battle, user, target):
    '''
    Returns the amount of damage done if user uses this move on target.
    '''
    level = float(2*user.lvl() + 10)/250
    stats = float(user.atk)/target.dfn
    stab = 1.5 if self.type in user.types else 1
    types = (type_effectiveness[self.type][type] for type in target.types)
    type_multiplier = reduce(operator.mul, types, 1)
    randomness = uniform(0.85, 1)
    return int((level*stats*self.power + 2)*stab*type_multiplier*randomness)

  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]
