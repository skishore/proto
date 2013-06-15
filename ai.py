from random import sample


class AI(object):
  @staticmethod
  def make_random_choices(battle):
    result = []
    for i in range(battle.num_npcs):
      user_id = ('npc', i)
      user = battle.get_pokemon(user_id)
      move = sample(user.moves, 1)[0]
      result.append({
        'type': 'move',
        'user_id': user_id,
        'move': move,
      })
      target_ids = move.get_target_ids(battle, user_id)
      if target_ids:
        result[-1]['target_id'] = sample(target_ids, 1)[0]
    return result
