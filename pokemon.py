from random import randint

from data import pokedex_data
from move import Move


class Pokemon(object):
  stats = ('atk', 'def', 'spa', 'spd', 'spe')

  def __init__(self, num, level=1):
    self.num = num
    self.level = level
    data = pokedex_data[num]
    self.name = data['name']
    self.max_hp = data['hp']
    self.cur_hp = self.max_hp
    for stat in self.stats:
      setattr(self, stat, data[stat])

  def apply_noise(self):
    for stat in self.stats:
      setattr(self, stat, getattr(self, stat) + randint(0, 15))

  @staticmethod
  def random_pokemon():
    pokemon = Pokemon(randint(1, 251), randint(1, 10))
    num_moves = randint(3, 4)
    pokemon.moves = Move.random_moves(num_moves)
    return pokemon
