types = set([
  'NORMAL',
  'FIGHTING',
  'FLYING',
  'POISON',
  'GROUND',
  'ROCK',
  'BUG',
  'GHOST',
  'STEEL',
  'FIRE',
  'WATER',
  'GRASS',
  'ELECTRIC',
  'PSYCHIC',
  'ICE',
  'DRAGON',
  'DARK',
])

#------ Parse the Pokemon data from pokemon.txt. -------#

pokedex_data = {}
raw_pokedex_data = open('data/pokemon.txt', 'r').read()

for (i, line) in enumerate(raw_pokedex_data.split('\r\n')[1:252]):
  row = line.split(',')
  assert(int(row[0]) == i + 1)
  pokemon = {
    'johto': int(row[1]),
    'name': row[2].upper(),
    'hp': int(row[3]),
    'atk': int(row[4]),
    'def': int(row[5]),
    'spa': int(row[6]),
    'spd': int(row[7]),
    'spe': int(row[8]),
    'types': tuple(t for t in row[9:11] if t != 'null'),
  }
  assert(all(t in types for t in pokemon['types'])), \
    'Unexpected types: %s' % (row[-2:],)
  pokedex_data[i + 1] = pokemon

assert(set(pokedex_data.iterkeys()) == set(xrange(1, 252)))
assert(set(
  row['johto'] for row in pokedex_data.itervalues()
) == set(xrange(1, 252)))

def get_front_index(pokenum):
  result = pokedex_data[pokenum]['johto']
  # Account for the fact that we have an extra Jynx sprite.
  if result > 153:
    result += 1
  return result - 1 

#------ Parse the move data from my_moves.txt. -------#

move_data = {}
raw_move_data = open('data/moves.txt', 'r').read()

for line in raw_move_data.split('\r\n')[1:-1]:
  row = line.split(',')
  assert(row[5] in types), 'Unexpected type: %s' % (row[5],)
  move_data[int(row[0])] = {
    'name': row[1].upper(),
    'accuracy': row[2],
    'power': row[3],
    'pp': row[4],
    'type': row[5],
  }
