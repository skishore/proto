import operator
from random import (
  sample,
  uniform,
)

from core import Callbacks
from data import (
  move_data,
  type_effectiveness,
  physical_types,
)


class Move(object):
  attrs = ('name', 'accuracy', 'power', 'type', 'extra')
  moves = move_data.keys()

  default_crit_rate = 0.0625

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
    if self.hits(battle, user, target):
      if self.get_type_advantage(target):
        (damage, message) = self.compute_damage(battle, user, target)
        callback = Callbacks.do_damage(battle, target_id, damage, message)
      else:
        result = ["It didn't affect %s!" % (battle.get_name(target_id, lower=True),)]
        callback = Callbacks.chain({'menu': result})
    else:
      result = ['It missed %s!' % (battle.get_name(target_id, lower=True),)]
      callback = Callbacks.chain({'menu': result})
    return {'menu': menu, 'callback': callback}

  def compute_damage(self, battle, user, target):
    '''
    Returns a pair:
      - the amount of damage done if user uses this move on target.
      - a message that describes modifies applied to that damage.
    '''
    crit = self.crit(battle, user, target)
    lvl_multiplier = 4 if crit else 2
    level = float(lvl_multiplier*user.lvl() + 10)/250
    stat_ratio = (
      float(user.atk)/target.dfn if self.type in physical_types else
      float(user.spa)/target.spd
    )
    stab = 1.5 if self.type in user.types else 1
    type_advantage = self.get_type_advantage(target)
    randomness = uniform(0.85, 1)
    return (
      int((level*stat_ratio*self.power + 2)*stab*type_advantage*randomness),
      ('Critical hit! ' if crit else '') + (self.get_type_message(battle, user, target))
    )

  def crit(self, battle, user, target):
    crit_rate = self.extra.get('crit_rate', self.default_crit_rate)
    return uniform(0, 1) < crit_rate

  def get_type_advantage(self, target):
    factors = (type_effectiveness[self.type][type] for type in target.types)
    return reduce(operator.mul, factors, 1)

  def get_type_message(self, battle, user, target):
    type_advantage = self.get_type_advantage(target)
    if type_advantage < 1:
      return "It's not very effective..."
    elif type_advantage > 1:
      return "It's super effective!"
    return ''

  def hits(self, battle, user, target):
    return uniform(0, 100) < self.accuracy

  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]
