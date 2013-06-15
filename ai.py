from random import sample


def make_ai_choices(battle):
  result = []
  for i in range(battle.num_npcs):
    user = ('npc', i)
    pokemon = battle.get_pokemon(user)
    move = sample(pokemon.moves, 1)[0]
    result.append({
      'type': 'move',
      'user': user,
      'move': move,
    })
    targets = move.get_targets(battle, user)
    if targets:
      result[-1]['target'] = sample(targets, 1)[0]
  return result
