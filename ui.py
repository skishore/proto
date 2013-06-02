from font import Font
from pokedex import (
  get_front_index,
  get_name,
)
from sprite import Sprite

screen_size = (420, 420)
back_size = 50
front_size = 56
row_space = 14

max_num_user_pokemon = 4
max_num_enemy_pokemon = 8

font_size = 8
max_name_length = 10
name_size = font_size*max_name_length

ui_height = 100

white = (255, 255, 255)
black = (0, 0, 0)


class BattleUI(object):
  def __init__(self):
    self.font = Font()
    self.user_sprite = self.get_sprite('pokemon_back_tiled.bmp')
    self.enemy_sprite = self.get_sprite('pokemon.bmp')

    # Dummy values to test the UI.
    import random
    self.user_pokemon = range(147, 150)
    self.enemy_pokemon = [
      41 + random.randrange(2) for i in range(7)
    ]

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
    surface.fill(white)
    self.draw_user_pokemon(surface)
    self.draw_enemy_pokemon(surface)

  def draw_user_pokemon(self, surface):
    top = screen_size[1] - ui_height - self.user_sprite.height - 3*font_size/2
    self.draw_pokemon_row(surface, self.user_pokemon, self.user_sprite, top)

  def draw_enemy_pokemon(self, surface):
    num = len(self.enemy_pokemon)
    top_row = num
    if num > max_num_enemy_pokemon/2:
      top_row = (num + 1)/2
    for row in xrange(2):
      pokemon = self.enemy_pokemon[row*top_row:(row + 1)*top_row]
      top = (row + 1)*row_space + row*(self.enemy_sprite.height + 3*font_size/2)
      shift = bool(row and (num % 2))
      self.draw_pokemon_row(surface, pokemon, self.enemy_sprite, top, shift)

  def draw_pokemon_row(self, surface, pokemon, sprite, top, shift=False):
    num = len(pokemon)
    total = screen_size[0] + name_size
    for (i, pokenum) in enumerate(pokemon):
      far_left = int((i + 1 + 0.5*shift)*total/(num + 1 + shift)) - name_size
      left = far_left + (name_size - font_size*len(get_name(pokenum)))/2
      self.font.draw(surface, get_name(pokenum), left, top + sprite.height + font_size/2)
      left = far_left + (name_size - sprite.width)/2
      sprite.set_position(left, top)
      sprite.set_pokenum(pokenum)
      sprite.draw(surface)
