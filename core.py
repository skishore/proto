class Core(object):
  @staticmethod
  def execute(battle, choices, done):
    '''
    Executes a single move and returns a (menus, callback) pair.
    The menus are displayed, and when they are emptied, the callback is called.

    This method updates the done set in place.
    '''
    assert(len(done) < len(choices))
    for index in battle.execution_order():
      if index not in done:
        done.add(index)
        assert(choices[index]['type'] == 'move')
        return Core.do_move(battle, index, choices[index])

  @staticmethod
  def do_move(battle, index, choice):
    '''
    Returns the actual result dict once the mover is chosen.
    '''
    menus = []
    callback = None
    (move, target) = (choice['move'], choice['target'])
    user = battle.get_pokemon(index)
    target = battle.get_pokemon(target)
    is_pc = (index[0] == 'pc')
    menus.append(['%s%s used %s on %s!' % (
      '' if is_pc else 'Enemy ', user.name, move.name, target.name,
    )])
    return (menus, callback)


class Callbacks(object):
  '''
  This class defines a number of static methods that return battle updates.
  These updates are functions with the same signature as Core.execute.
  '''
  @staticmethod
  def faint(indices):
    def update(battle, choices, done):
      print 'The following indices fainted: %s' % (indices,)
