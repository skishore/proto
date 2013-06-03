from pokedex import random_pokemon


class Battle(object):
  def __init__(self):
    self.user_pokemon = [random_pokemon() for i in xrange(3)]
    self.enemy_pokemon = [random_pokemon() for i in xrange(7)]
    self.state = Battle.Initialize(self)

  def transition(self, keys):
    '''
    Transition functions should return a (new_state, update) pair,
    where update is a boolean which is True if state changed.
    '''
    (self.state, result) = self.state.transition(keys)
    return result

  def get_menu(self):
    return self.state.get_menu()

  class Initialize(object):
    '''
    Initial state. For now, immediately transitions to choosing a move.
    '''
    def __init__(self, battle):
      self.battle = battle

    def transition(self, keys):
      return (Battle.ChooseMove(self.battle, 0), True)

    def get_menu(self):
      return []

  class ChooseMove(object):
    '''
    Choose a move for the `index`th user pokemon.
    '''
    def __init__(self, battle, index):
      self.battle = battle
      self.index = index

    def transition(self, keys):
      return (self, False)

    def get_menu(self):
      return [
        'What will %s do?' % (self.battle.user_pokemon[self.index].name,),
      ]
