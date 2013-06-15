class Core(object):
  @staticmethod
  def execute(battle, choices):
    '''
    Executes a single move and returns a (menus, callback) pair.
    The menus are displayed, and when they are emptied, the callback is called.

    This method may update the battle and the set of remaining choices.
    '''
    assert(choices)
    for index in battle.execution_order():
      if index in choices:
        choice = choices.pop(index)
        assert(choice['type'] == 'move')
        return Core.do_move(battle, index, choice)

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
    def update(battle, choices):
      print 'The following indices fainted: %s' % (indices,)
