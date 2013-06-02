from random import randint

from data import pokedex_data

assert(set(pokedex_data.iterkeys()) == set(xrange(1, 252)))
assert(
  set(row['johto'] for row in pokedex_data.itervalues()
) == set(xrange(1, 252)))


def get_front_index(pokenum):
  result = pokedex_data[pokenum]['johto']
  # Account for the fact that we have an extra Jynx sprite.
  if result > 153:
    result += 1
  return result - 1


class Pokemon(object):
  def __init__(self, num, level=1):
    self.num = num
    self.level = level
    self.name = pokedex_data[num]['name']
    self.health = 1.0


def random_pokemon():
  pokemon = Pokemon(randint(1, 251), randint(1, 10))
  pokemon.health = 1.0*randint(1, 100)/100
  return pokemon
