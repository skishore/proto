import operator
from random import (
  randrange,
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
    menu = ['%s used %s!' % (battle.get_name(user_id), self.name)]
    move_type = self.extra.get('move_type', 'default')
    callback = getattr(self, 'execute_' + move_type)(battle, user_id, target_id)
    return {'menu': menu, 'callback': callback}

  '''
  Move execution methods begin here. All move execution methods should return
  a callback to be executed after the '<user> used <move>!' text is shown.
  '''

  def execute_default(self, battle, user_id, target_id, cur_hit=0, num_hits=0):
    '''
    An implementation of a damaging, single-target move.
    '''
    user = battle.get_pokemon(user_id)
    target = battle.get_pokemon(target_id)
    if num_hits or self.hits(battle, user, target):
      if self.get_type_advantage(target):
        (damage, message) = self.compute_damage(battle, user, target)
        callback = None
        if num_hits:
          callback = self.execute_multihit(battle, user_id, target_id, cur_hit, num_hits)
        return Callbacks.do_damage(battle, target_id, damage, message, callback=callback)
      else:
        menu = ["It didn't affect %s!" % (battle.get_name(target_id, lower=True),)]
        return Callbacks.chain({'menu': menu})
    else:
      menu = ['It missed %s!' % (battle.get_name(target_id, lower=True),)]
      return Callbacks.chain({'menu': menu})

  def execute_multihit(self, battle, user_id, target_id, cur_hit=0, num_hits=0):
    '''
    A move that, if it hits, strikes the target 2-5 times.
    '''
    if not num_hits:
      user = battle.get_pokemon(user_id)
      target = battle.get_pokemon(target_id)
      if self.hits(battle, user, target):
        hits_map = {0: 2, 1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 4, 7: 5}
        num_hits = hits_map[randrange(8)]
      else:
        menu = ['It missed %s!' % (battle.get_name(target_id, lower=True),)]
        return Callbacks.chain({'menu': menu})
    if cur_hit < num_hits:
      return self.execute_default(battle, user_id, target_id, cur_hit + 1, num_hits)
    return Callbacks.chain({'menu': ['Hit %s times!' % (num_hits,)]})

  '''
  Auxilary methods that perform damage computation, etc. begin here.
  '''

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
    crit_rate = self.extra.get('crit_rate', 0.0625)
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
  def latest_moves(num_moves=4):
    move_numbers = sorted(move_data.iterkeys(), reverse=True)
    return [Move(num) for num in move_numbers[:num_moves]]

  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]
