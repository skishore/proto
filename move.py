import operator
from random import (
  randrange,
  sample,
  uniform,
)

from core import Callbacks
from data import (
  move_data,
  Stat,
  Status,
  Type,
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
    target = self.extra.get('target', 'default')
    if target == 'default':
      if index[0] == 'npc':
        return [('pc', i) for i in range(battle.num_pcs)]
      return [('npc', i) for i in range(battle.num_npcs)]
    elif target == 'self':
      return []
    assert(False), 'Unexpected target: %s' % (target,)

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
    if self.get_type_advantage(target):
      if num_hits or self.hits(battle, user, target):
        (damage, message) = self.compute_damage(battle, user, target)
        callback = None
        if num_hits:
          callback = self.execute_multihit(battle, user_id, target_id, cur_hit, num_hits)
        callback = self.get_secondary_effect(battle, target_id, target, callback)
        return Callbacks.do_damage(battle, target_id, damage, message, callback=callback)
      else:
        return self.execute_miss(battle, user_id, target_id)
    else:
      message = "It didn't affect %s!" % (battle.get_name(target_id, lower=True),)
      return self.execute_miss(battle, user_id, target_id, message=message)

  def execute_multihit(self, battle, user_id, target_id, cur_hit=0, num_hits=0):
    '''
    A move that, if it hits, strikes the target 2-5 times.
    '''
    if not num_hits:
      user = battle.get_pokemon(user_id)
      target = battle.get_pokemon(target_id)
      if self.get_type_advantage(target):
        if self.hits(battle, user, target):
          if 'num_hits' in self.extra:
            num_hits = self.extra['num_hits']
          else:
            hits_map = {0: 2, 1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 4, 7: 5}
            num_hits = hits_map[randrange(8)]
        else:
          return self.execute_miss(battle, user_id, target_id)
      else:
        message = "It didn't affect %s!" % (battle.get_name(target_id, lower=True),)
        return self.execute_miss(battle, user_id, target_id, message=message)
    if cur_hit < num_hits:
      return self.execute_default(battle, user_id, target_id, cur_hit + 1, num_hits)
    return Callbacks.chain({'menu': ['Hit %s times!' % (num_hits,)]})

  def execute_miss(self, battle, user_id, target_id, message=None):
    message = message or 'But it missed!'
    if 'miss_penalty' in self.extra:
      user = battle.get_pokemon(user_id)
      damage = -(-user.cur_hp/8)
      return Callbacks.do_damage(battle, user_id, damage, message, special=' instead')
    return Callbacks.chain({'menu': [message or 'But it missed!']})

  def execute_buff(self, battle, user_id, target_id):
    (stat, stages) = (self.extra['stat'], self.extra['stages'])
    assert(stat in Stat.OPTIONS and stat != Stat.HP and abs(stages) in (1, 2)), \
      'Unexpected buff: (%s, %s)' % (stat, stages)
    user = battle.get_pokemon(user_id)
    if self.extra.get('target') == self:
      target_id = user_id
      target = user
    else:
      assert(stages < 0), 'Unexpected buff on enemy: %s' % (self.name,)
      target = battle.get_pokemon(target_id)
      if not self.hits(battle, user, target):
        return self.execute_miss(battle, user_id, target_id)
    return Callbacks.do_buff(battle, target_id, stat, stages)

  def execute_status(self, battle, user_id, target_id):
    status = self.extra['status']
    assert(status in Status.OPTIONS), 'Unexpected status: %s' % (status,)
    user = battle.get_pokemon(user_id)
    target = battle.get_pokemon(target_id)
    if self.hits(battle, user, target):
      return Callbacks.set_status(battle, target_id, status, self, noisy_failure=True)
    return self.execute_miss(battle, user_id, target_id)

  '''
  Auxilary methods that perform damage computation, etc. begin here.
  '''

  def compute_damage(self, battle, user, target):
    '''
    Returns a pair:
      - the amount of damage done if user uses this move on target.
      - a message that describes modifies applied to that damage.
    '''
    if 'damage' in self.extra:
      return (self.extra['damage'], None)
    crit = self.crit(battle, user, target)
    lvl_multiplier = 4 if crit else 2
    level = float(lvl_multiplier*user.lvl() + 10)/250
    stat_ratio = (
      float(user.stat(Stat.ATTACK))/target.stat(Stat.DEFENSE) if self.type in Type.PHYSICAL_TYPES else
      float(user.stat(Stat.SPECIAL_ATTACK))/target.stat(Stat.SPECIAL_DEFENSE)
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
    if 'damage' in self.extra:
      return 1
    factors = (Type.TYPE_EFFECTIVENESS[self.type][type] for type in target.types)
    return reduce(operator.mul, factors, 1)

  def get_type_message(self, battle, user, target):
    type_advantage = self.get_type_advantage(target)
    if type_advantage < 1:
      return "It's not very effective..."
    elif type_advantage > 1:
      return "It's super effective!"
    return ''

  def hits(self, battle, user, target):
    return uniform(0, 100) < self.accuracy*user.stat(Stat.ACCURACY)/target.stat(Stat.EVASION)

  def get_secondary_effect(self, battle, target_id, target, callback):
    stat_rate = self.extra.get('stat_rate')
    if stat_rate and uniform(0, 1) < stat_rate:
      (stat, stages) = (self.extra['stat'], self.extra['stages'])
      callback = Callbacks.do_buff(battle, target_id, stat, stages, callback=callback)
    for status in Status.OPTIONS:
      rate = self.extra.get(status + '_rate')
      if rate and uniform(0, 1) < rate:
        callback = Callbacks.set_status(battle, target_id, status, self, callback=callback)
    return callback

  @staticmethod
  def latest_moves(num_moves=4):
    move_numbers = sorted(move_data.iterkeys(), reverse=True)
    return [Move(num) for num in move_numbers[:num_moves]]

  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]


class ConfusedMove(Move):
  def __init__(self):
    self.power = 40
    self.type = None

  def crit(self, battle, user, target):
    return False

  def get_type_advantage(self, target):
    return 1
ConfusedMove = ConfusedMove()
