from random import randrange


def make_ai_choices(battle):
  result = []
  for (i, pokemon) in enumerate(battle.enemy_pokemon):
    result.append({
      'type': 'move',
      'poke': i,
      'move': randrange(len(pokemon.moves)),
      'target': randrange(len(battle.user_pokemon)),
    })
  return result
