def do_moves(battle, choices):
  '''
  Executes the given moves in the order of the monster's speeds.
  '''
  choices = {choice['user']: choice for choice in choices}
  done = set()
  fainted = set()
  result = []
  # Recompute the execution order for each move to account for changes in speed.
  while len(done) < len(choices):
    for index in battle.execution_order():
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
        move.name,
      )],
    })
  return result


class Updates(object):
  '''
  This class defines a number of static methods that apply updates to a battle.
  Each of these methods should return a function that takes a battle and mutates it.
  '''
  @staticmethod
  def faint(indices):
    def update(battle):
      print 'The following indices fainted: %s' % (indices,)
