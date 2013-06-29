from random import randint

from data import pokedex_data
from move import Move


level_multiplier = 10
num_pokemon = 251


class Pokemon(object):
  stats = ('hp', 'atk', 'dfn', 'spa', 'spd', 'spe')

  def __init__(self, num, level=1):
    self.num = num
    self.level = level
    self.name = pokedex_data[num]['name']
    self.types = pokedex_data[num]['types']
    self.status = None
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
    value = getattr(self, stat)
    if stat == 'atk' and self.status == 'burn':
      return value/2
    return value

  @staticmethod
  def random_pokemon(side):
    pokemon = Pokemon(randint(1, num_pokemon), randint(1, 2))
    if side == 'pc':
      pokemon.moves = Move.latest_moves(4)
    else:
      num_moves = randint(2, 3)
      pokemon.moves = Move.random_moves(num_moves)
    return pokemon
