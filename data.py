import json

#----- A bunch of enumerations. ------#

class Stat(object):
  HP = 'hp'
  ATTACK = 'attack'
  DEFENSE = 'defense'
  SPECIAL_ATTACK = 'special attack'
  SPECIAL_DEFENSE = 'special defense'
  SPEED = 'speed'
  ACCURACY = 'accuracy'
  EVASION = 'evasion'

  OPTIONS = (
    HP,
    ATTACK,
    DEFENSE,
    SPECIAL_ATTACK,
    SPECIAL_DEFENSE,
    SPEED,
    ACCURACY,
    EVASION,
  )


class Status(object):
  BURN = 'burn'
  POISON = 'poison'
  PARALYZE = 'paralyze'
  FREEZE = 'freeze'
  SLEEP = 'sleep'
  FLINCH = 'flinch'

  OPTIONS = (
    BURN,
    POISON,
    PARALYZE,
    FREEZE,
    SLEEP,
    FLINCH,
  )

  SOFT_STATUSES = (
    FLINCH,
  )

  MARKS = {
    BURN: 'B',
    POISON: 'P',
    PARALYZE: 'R',
    FREEZE: 'F',
    SLEEP: 'S',
  }

  VERBS = {
    BURN: 'was burned',
    POISON: 'was poisoned',
    PARALYZE: 'was paralyzed',
    FREEZE: 'was frozen solid',
    SLEEP: 'fell asleep',
    FLINCH: 'flinched',
  }

#------ Parse the type data from types.txt. -------#

num_types = 17

with open('data/types.txt', 'r') as types_txt:
  raw_type_data = types_txt.read()
lines = raw_type_data.split('\n')
assert(len(lines) == 2*num_types + 4)

types = ()
physical_types = ()
special_types = ()

for line in lines[1:num_types + 1]:
  (type, ph_or_sp) = line.split()
  assert(type.isalpha() and type == type.upper())
  types += (type,)
  assert(ph_or_sp in ('ph', 'sp'))
  if ph_or_sp == 'ph':
    physical_types += (type,)
  else:
    special_types += (type,)
assert(len(types) == num_types)

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
    'attack': int(row[4]),
    'defense': int(row[5]),
    'special attack': int(row[6]),
    'special defense': int(row[7]),
    'speed': int(row[8]),
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

for line in raw_move_data.split('\r\n')[:-1]:
  if line.startswith('#'):
    continue
  row = line.split(',')
  assert(row[5] in types), 'Unexpected type: %s' % (row[5],)
  move = {
    'name': row[1].upper(),
    'accuracy': int(row[2]),
    'power': int(row[3]),
    'pp': int(row[4]),
    'type': row[5],
    'extra': json.loads(','.join(row[6:])) if len(row) > 6 else {}
  }
  for (key, value) in move['extra'].iteritems():
    if key not in ('move_type', 'miss_penalty', 'num_hits', 'target', 'stat', 'stages'):
      assert(key.endswith('_rate')), 'Unexpected key: %s' % (key,)
      status = key[:-5]
      if status not in ('crit',):
        assert(status in Status.OPTIONS), 'Unexpected status: %s' % (status,)
    elif key == 'stat':
      assert(value in Stat.OPTIONS), 'Unexpected stat: %s' % (value,)
  move_data[int(row[0])] = move
