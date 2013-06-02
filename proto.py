import pygame
import sys
import time

from font import Font
from key_repeater import KeyRepeater
from pokedex import get_front_index
from sprite import Sprite

framerate = 24
delay = 1.0/framerate

screen_size = (480, 320)

white = (255, 255, 255)
black = (0, 0, 0)
teal = (128, 192, 255)


class TestGame(object):
  def __init__(self):
    self.screen = pygame.display.set_mode(screen_size)
    self.font = Font()
    self.key_repeater = self.construct_key_repeater()

    self.backs = self.get_sprite('pokemon_back_tiled.bmp')
    self.backs.set_position(60, 60)
    self.fronts = self.get_sprite('pokemon.bmp')
    self.fronts.set_position(120, 60)

    self.set_pokenum()

  @staticmethod
  def construct_key_repeater():
    return KeyRepeater(
      one_time_keys=(
        pygame.K_ESCAPE,
      ),
      repeated_keys=(
        pygame.K_UP,
        pygame.K_RIGHT,
        pygame.K_DOWN,
        pygame.K_LEFT,
      ),
      pause=framerate/4,
      repeat=framerate/8,
    )

  @staticmethod
  def get_sprite(filename):
    if filename == 'pokemon.bmp':
      return Sprite(
        filename,
        width=56,
        height=56,
        cols=10,
        rows=26,
        offset=(8, 24),
        period=(64, 64),
      )
    elif filename == 'pokemon_back_tiled.bmp':
      return Sprite(
        filename,
        width=50,
        height=50,
        cols=7,
        rows=36,
        offset=(6, 6),
        period=(54, 57),
      )
    assert(False), 'Unexpected image name: %s' % (filename,)

  def set_pokenum(self, pokenum=1):
    if pokenum <= 0 or pokenum > 251:
      return
    self.pokenum = pokenum
    self.fronts.set_index(get_front_index(pokenum))
    self.backs.set_index(pokenum - 1)

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
      self.key_repeater.handle_event(event)
    keys = self.key_repeater.query()
    if pygame.K_ESCAPE in keys:
      sys.exit()
    if pygame.K_RIGHT in keys or pygame.K_DOWN in keys:
      self.set_pokenum(self.pokenum + 1)
    elif pygame.K_LEFT in keys or pygame.K_UP in keys:
      self.set_pokenum(self.pokenum - 1)

  def draw_text(self, text, x, y, color):
    text_surface = self.font.render(text, 1, color)
    self.screen.blit(text_surface, (x, y))

  def draw(self):
    self.screen.fill(teal)
    self.fronts.draw(self.screen)
    self.backs.draw(self.screen)
    self.font.draw(self.screen, 'Testing: the @# font 2000 v1.1. (huzzah!)', 40, 40)
    pygame.display.flip()

  def game_loop(self):
    while True:
      self.handle_events()
      self.draw()
      time.sleep(delay)

if __name__ == '__main__':
  pygame.init()
  game = TestGame()
  game.game_loop()
