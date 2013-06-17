#------ Parse the type data from types.txt. -------#

num_types = 17

with open('data/types.txt', 'r') as types_txt:
  raw_type_data = types_txt.read()
lines = raw_type_data.split('\n')
assert(len(lines) == 2*num_types + 4)

types = tuple(lines[1:num_types + 1])
for type in types:
  assert(type and type.isalnum())

def parse_effectiveness(char):
  assert(char in (' ', '0', '2') or ord(char) == 189)
  if ord(char) == 189:
    return 0.5
  return {' ': 1, '0': 0, '2': 2}[char]

type_effectiveness = {}
for (source, line) in zip(types, lines[num_types + 3:]):
  decoded = line.decode('utf8')
  assert(len(decoded) == 17)
  type_effectiveness[source] = {
    target: parse_effectiveness(char) for (target, char) in zip(types, decoded)
  }
  assert(all(type in type_effectiveness[source] for type in types))
assert(all(type in type_effectiveness for type in types))


#------ Parse the Pokemon data from pokemon.txt. -------#

pokedex_data = {}
with open('data/pokemon.txt', 'r') as pokemon_txt:
  raw_pokedex_data = pokemon_txt.read()

for (i, line) in enumerate(raw_pokedex_data.split('\r\n')[1:252]):
  row = line.split(',')
  assert(int(row[0]) == i + 1)
  pokemon = {
    'johto': int(row[1]),
    'name': row[2].upper(),
    'hp': int(row[3]),
    'atk': int(row[4]),
    'dfn': int(row[5]),
    'spa': int(row[6]),
    'spd': int(row[7]),
    'spe': int(row[8]),
    'types': tuple(t for t in row[9:11] if t != 'null'),
  }
  assert(all(t in types for t in pokemon['types'])), \
    'Unexpected types: %s' % (pokemon['types'],)
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
with open('data/moves.txt', 'r') as moves_txt:
  raw_move_data = moves_txt.read()

for line in raw_move_data.split('\r\n')[1:-1]:
  row = line.split(',')
  assert(row[5] in types), 'Unexpected type: %s' % (row[5],)
  move_data[int(row[0])] = {
    'name': row[1].upper(),
    'accuracy': int(row[2]),
    'power': int(row[3]),
    'pp': int(row[4]),
    'type': row[5],
  }
