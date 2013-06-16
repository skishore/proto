import math
import pygame

from data import get_front_index
from font import Font
from sprite import Sprite

draw_sprites = True

screen_size = (360, 300)
back_size = 50
front_size = 56

max_num_pc_pokemon = 3
max_num_npc_pokemon = 3

font_size = 8
max_name_length = 10

name_size = font_size*max_name_length
top_row_space = font_size
status_height = 4*font_size
health_border = (1, 6)
health_bar = (
  name_size - 7*font_size/2 - 2*health_border[0],
  health_border[1] - 2
)

ui_height = 9*font_size

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (224, 224, 0)
green = (0, 255, 0)


class BattleUI(object):
  def __init__(self):
    self.font = Font()
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

  def draw(self, surface, battle):
    surface.fill(white)
    display = battle.get_display()
    self.draw_pc_pokemon(surface, battle.all_pcs(), display)
    self.draw_npc_pokemon(surface, battle.all_npcs(), display)
    self.draw_menu(surface, display['menu'])

  def draw_pc_pokemon(self, surface, pc_pokemon, display):
    top = screen_size[1] - ui_height - self.user_sprite.height - status_height
    self.draw_pokemon_row(surface, pc_pokemon, top, 'pc', display)

  def draw_npc_pokemon(self, surface, npc_pokemon, display):
    self.draw_pokemon_row(surface, npc_pokemon, top_row_space, 'npc', display)

  def draw_pokemon_row(self, surface, pokemon_list, top, side, display):
    num = len(pokemon_list)
    total = screen_size[0] + name_size
    sprite = self.user_sprite if side == 'pc' else self.enemy_sprite
    for (i, pokemon) in enumerate(pokemon_list):
      left = int((i + 1)*total/(num + 1)) - name_size
      self.draw_pokemon(surface, sprite, pokemon, left, top, (side, i), display)

  def draw_pokemon(self, surface, sprite, pokemon, far_left, top, index, display):
    # Draw the Pokemon's (back or front) sprite.
    left = far_left + (name_size - sprite.width)/2
    sprite.set_position(left, top)
    sprite.set_pokenum(pokemon.num)
    if draw_sprites and index not in display.get('hidden_indices', ()):
      sprite.draw(surface)
    # Draw the Pokemon's name.
    name = pokemon.name
    left = far_left + (name_size - font_size*len(name))/2
    top += (sprite.height + font_size/2)/(1 if draw_sprites else 2)
    self.font.draw(surface, name, left, top)
    # Draw the Pokemon's level.
    offset = (pokemon.level < 10)*font_size/2
    top += 3*font_size/2
    self.font.draw(surface, 'L%d' % (pokemon.level,), far_left + offset, top)
    # Draw the Pokemon's health bar.
    left = far_left + 7*font_size/2 - offset
    top += font_size/2
    health = float(pokemon.cur_hp)/pokemon.max_hp
    self.draw_health_bar(surface, health, left, top)

  def draw_health_bar(self, surface, health, left, top):
    # Draw the left and right borders of the health bar.
    pygame.draw.rect(surface, black, (
      left,
      top - health_border[1]/2,
      health_border[0],
      health_border[1],
    ))
    pygame.draw.rect(surface, black, (
      left + health_border[0] + health_bar[0],
      top - health_border[1]/2,
      health_border[0],
      health_border[1],
    ))
    # Draw a line underneath the bar. This code may be incorrect...
    pygame.draw.line(surface, black, (
      left + health_border[0],
      top + health_border[1]/2 - health_bar[1]/2 + 1,
    ), (
      left + health_border[0] + health_bar[0],
      top + health_border[1]/2 - health_bar[1]/2 + 1,
    ))
    # Draw the actual health bar in the correct color.
    color = green if health > 0.5 else yellow if health > 0.25 else red
    width = int(math.ceil(health*health_bar[0]))
    if width:
      pygame.draw.rect(surface, color, (
        left + health_border[0],
        top - health_bar[1]/2,
        width,
        health_bar[1],
      ))

  def draw_menu(self, surface, menu):
    self.draw_menu_block(surface, menu, 0, screen_size[0])

  def draw_menu_block(self, surface, lines, left, width):
    pygame.draw.rect(surface, black, (
      left,
      screen_size[1] - ui_height,
      width,
      ui_height,
    ), 1)
    top = screen_size[1] - ui_height + font_size
    for line in lines:
      self.font.draw(surface, line, left + font_size, top)
      top += 3*font_size/2
