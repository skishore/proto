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


def get_name(pokenum):
  return pokedex_data[pokenum]['name']
