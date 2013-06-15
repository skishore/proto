from collections import defaultdict
from random import sample


def do_moves(battle, user_choices, enemy_choices):
  '''
  Executes the given moves in the order of the monster's speeds.
  '''
  choices = dict((('user', i), choice) for (i, choice) in enumerate(user_choices))
  choices.update((('enemy', i), choice) for (i, choice) in enumerate(enemy_choices))
  # done is a list of monsters that have either moved or have fainted.
  # fainted is a list of the ones that have fainted.
  done = set()
  fainted = set()
  result = []
  # Recompute the execution order for each move to account for changes in speed.
  while len(done) < len(choices):
    for index in execution_order(battle.user_pokemon, battle.enemy_pokemon):
      if index not in done:
        done.add(index)
        assert(choices[index]['type'] == 'move')
        result.extend(do_move(battle, index, choices[index], fainted))
  if fainted:
    result.append({'execute': Updates.faint(fainted)})
  return result


def do_move(battle, index, choice, fainted):
  result = []
  if index not in fainted:
    pokemon = battle.get_pokemon(index)
    (move, target) = (choice['move'], choice['target'])
    is_user = (index[0] == 'user')
    target = ('enemy' if is_user else 'user', target)
    result.append({
      'menu': ['%s%s used %s!' % (
        '' if is_user else 'Enemy ',
        pokemon.name,
        pokemon.moves[move]['name'],
      )],
    })
  return result


def execution_order(user_pokemon, enemy_pokemon):
  speeds = defaultdict(list)
  for (i, pokemon) in enumerate(user_pokemon):
    speeds[pokemon.spe].append(('user', i))
  for (i, pokemon) in enumerate(enemy_pokemon):
    speeds[pokemon.spe].append(('enemy', i))
  for speed in speeds:
    speeds[speed] = sample(speeds[speed], len(speeds[speed]))
  return sum((speeds[speed] for speed in sorted(speeds.iterkeys())), [])


class Updates(object):
  '''
  This class defines a number of static methods that apply updates to a battle.
  Each of these methods should return a function that takes a battle and mutates it.
  '''
  @staticmethod
  def faint(indices):
    def update(battle):
      print 'The following indices fainted: %s' % (indices,)
