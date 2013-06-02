from font import Font
from pokedex import get_front_index
from sprite import Sprite

screen_size = (320, 320)
back_size = 50
front_size = 56
row_space = 8

max_num_user_pokemon = 4
max_num_enemy_pokemon = 8

white = (255, 255, 255)
black = (0, 0, 0)


class BattleUI(object):
  def __init__(self):
    self.user_sprite = self.get_sprite('pokemon_back_tiled.bmp')
    self.enemy_sprite = self.get_sprite('pokemon.bmp')

  @staticmethod
  def get_sprite(filename):
    if filename == 'pokemon_back_tiled.bmp':
      sprite = Sprite(
        filename,
        width=back_size,
        height=back_size,
        cols=7,
        rows=36,
        offset=(6, 6), 
        period=(54, 57),
      )
      sprite.set_pokenum = lambda i: sprite.set_index(i - 1)
    elif filename == 'pokemon.bmp':
      sprite = Sprite(
        filename,
        width=front_size,
        height=front_size,
        cols=10,
        rows=26,
        offset=(8, 24),
        period=(64, 64),
      )
      sprite.set_pokenum = lambda i: sprite.set_index(get_front_index(i))
    else:
      assert(False), 'Unexpected image name: %s' % (filename,)
    return sprite

  def draw(self, surface):
    # Dummy values to test the UI.
    self.user_pokemon = range(147, 150)
    self.enemy_pokemon = range(67, 75)

    surface.fill(white)
    self.draw_user_pokemon(surface)
    self.draw_enemy_pokemon(surface)

  def draw_user_pokemon(self, surface):
    top = screen_size[1]/2
    self.draw_pokemon_row(surface, self.user_pokemon, self.user_sprite, top)

  def draw_enemy_pokemon(self, surface):
    num = len(self.enemy_pokemon)
    top_row = num
    if num > max_num_enemy_pokemon/2:
      top_row = (num + 1)/2
    for row in xrange(2):
      pokemon = self.enemy_pokemon[row*top_row:(row + 1)*top_row]
      top = (row + 1)*row_space + row*self.enemy_sprite.height
      shift = bool(row and (num % 2))
      self.draw_pokemon_row(surface, pokemon, self.enemy_sprite, top, shift)

  def draw_pokemon_row(self, surface, pokemon, sprite, top, shift=False):
    num = len(pokemon)
    width = screen_size[0] + sprite.width
    for (i, pokenum) in enumerate(pokemon):
      left = int((i + 1 + 0.5*shift)*width/(num + 1 + shift)) - sprite.width
      sprite.set_position(left, top)
      sprite.set_pokenum(pokenum)
      sprite.draw(surface)
