from random import sample

from core import Callbacks
from data import move_data


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
    return (menu, callback)

  def compute_damage(self, battle, user, target):
    '''
    Returns the amount of damage done if user uses this move on target.
    '''
    # A placeholder implementation of a damaging, single-target move.
    return self.power/4

  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]
