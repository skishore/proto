class Core(object):
  @staticmethod
  def execute(battle, choices, done):
    '''
    Executes a single move and returns a (result, done) pair.
    The result is a dictionary with the following keys:
      menu: a list of menus to display to the user
      execute: a callback to execute when the user acks the move
    '''
    assert(len(done) < len(choices))
    for index in battle.execution_order():
      if index not in done:
        done.add(index)
        assert(choices[index]['type'] == 'move')
        return (Core.do_move(battle, index, choices[index]), done)

  @staticmethod
  def do_move(battle, index, choice):
    '''
    Returns the actual result dict once the mover is chosen.
    '''
    result = {}
    (move, target) = (choice['move'], choice['target'])
    user = battle.get_pokemon(index)
    target = battle.get_pokemon(target)
    is_pc = (index[0] == 'pc')
    result['menu'] = [[
      '%s%s used %s on %s!' % ('' if is_pc else 'Enemy ', user.name, move.name, target.name),
    ]]
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
