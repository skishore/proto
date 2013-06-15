from random import sample

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

  def get_targets(self, battle, user):
    # A placeholder implementation.
    # Some moves might target user pokemon, or have no target at all.
    if user[0] == 'pc':
      return [('npc', i) for i in range(battle.num_npcs)]
    return [('pc', i) for i in range(battle.num_pcs)]


  @staticmethod
  def random_moves(num_moves):
    return [Move(num) for num in sample(Move.moves, num_moves)]
