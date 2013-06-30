from random import randint

from data import pokedex_data
from move import Move


level_multiplier = 10
num_pokemon = 251


class Pokemon(object):
  stats = ('hp', 'atk', 'dfn', 'spa', 'spd', 'spe')

  # Set up stat multipliers based on the number of stages of buff.
  default_buffs = {}
  accuracy_buffs = {}
  for i in range(0, 7):
    default_buffs[i] = (2.0 + i)/2
    default_buffs[-i] = 2.0/(2 + i)
    accuracy_buffs[i] = (3.0 + i)/3
    accuracy_buffs[-i] = 3.0/(3 + i)

  def __init__(self, num, level=1):
    self.num = num
    self.level = level
    self.name = pokedex_data[num]['name']
    self.types = pokedex_data[num]['types']
    self.status = None
    self.soft_status = {}
    self.compute_stats()

  def compute_stats(self):
    self.ivs = getattr(self, 'ivs', {})
    for stat in self.stats:
      self.ivs[stat] = self.ivs.get(stat, randint(0, 15))
      setattr(self, stat, self.compute_stat(stat))
    self.max_hp = self.hp
    self.cur_hp = self.hp
    del self.hp

  def compute_stat(self, stat):
    lvl = self.lvl()
    base_plus_iv = pokedex_data[self.num][stat] + self.ivs[stat]
    if stat == 'hp':
      return (base_plus_iv + 50)*lvl/50 + 10
    return base_plus_iv*lvl/50 + 5

  def lvl(self):
    return level_multiplier*self.level

  def stat(self, stat):
    if stat in self.stats:
      value = getattr(self, stat)
      value *= self.default_buffs[self.soft_status.get(stat, 0)]
      if stat == 'atk' and self.status == 'burn':
        return int(0.50*value)
      elif stat == 'spe' and self.status == 'paralyze':
        return int(0.75*value)
      return value
    else:
      assert(stat in ('acc', 'eva'))
      return self.accuracy_buffs[self.soft_status.get(stat, 0)]

  @staticmethod
  def random_pokemon(side):
    pokemon = Pokemon(randint(1, num_pokemon), randint(1, 2))
    if side == 'pc':
      pokemon.moves = Move.latest_moves(4)
    else:
      num_moves = randint(2, 3)
      pokemon.moves = Move.random_moves(num_moves)
    return pokemon
