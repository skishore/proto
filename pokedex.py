from random import (
  randint,
  sample,
)

from data import (
  move_data,
  pokedex_data,
)

assert(set(pokedex_data.iterkeys()) == set(xrange(1, 252)))
assert(
  set(row['johto'] for row in pokedex_data.itervalues()
) == set(xrange(1, 252)))
moves = move_data.keys()

def get_front_index(pokenum):
  result = pokedex_data[pokenum]['johto']
  # Account for the fact that we have an extra Jynx sprite.
  if result > 153:
    result += 1
  return result - 1


class Pokemon(object):
  stats = ('atk', 'def', 'spa', 'spd', 'spe')

  def __init__(self, num, level=1):
    self.num = num
    self.level = level
    self.name = pokedex_data[num]['name']
    self.max_hp = pokedex_data[num]['hp']
    self.cur_hp = self.max_hp
    for stat in self.stats:
      setattr(self, stat, pokedex_data[num][stat])

  def apply_noise(self):
    for stat in self.stats:
      setattr(self, stat, getattr(self, stat) + randint(0, 15))

def random_pokemon():
  pokemon = Pokemon(randint(1, 251), randint(1, 10))
  num_moves = randint(3, 4)
  pokemon.moves = [dict(move_data[m]) for m in sample(moves, num_moves)]
  return pokemon
