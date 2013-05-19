import pygame
from pygame.rect import Rect
import random
import sys
import time

from key_repeater import KeyRepeater
from sprite import Sprite


framerate = 60
delay = 1.0/framerate

sq = 16
cols = 16
rows = 16
screen_size = (sq*cols, sq*rows)
start = (cols/2, rows/2)

speed = 2
tolerance = 0.2*sq
pushaway = 0.6*sq

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 128, 255)


class TestGame(object):
  def __init__(self):
    self.screen = pygame.display.set_mode(screen_size)
    self.key_repeater = self.construct_key_repeater()
    self.tilemap = self.generate_tilemap()
    self.sprite = Sprite(sq, start, blue)

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
    )

  @staticmethod
  def generate_tilemap():
    tilemap = [[
      random.randrange(5) == 0
      for j in range(rows)
    ] for i in range(cols)]
    tilemap[start[0]][start[1]] = 0
    return tilemap

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
      self.key_repeater.handle_event(event)
    keys = self.key_repeater.query()
    if pygame.K_ESCAPE in keys:
      sys.exit()
    self.sprite.velocity = [
      speed*((pygame.K_RIGHT in keys) - (pygame.K_LEFT in keys)),
      speed*((pygame.K_DOWN in keys) - (pygame.K_UP in keys)),
    ]

  def is_square_blocked(self, square):
    if (
      square[0] < 0 or square[0] >= len(self.tilemap) or
      square[1] < 0 or square[1] >= len(self.tilemap[0])
    ):
      return True
    return self.tilemap[square[0]][square[1]]
  
  def move_sprite(self, sprite):
    sprite.normalize(speed)
    sprite.handle_blocks(self.is_square_blocked, tolerance, pushaway)
    sprite.move()

  def draw(self):
    self.screen.fill(white)
    for i in range(cols):
      for j in range(rows):
        if self.tilemap[i][j]:
          square = Rect(sq*i, sq*j, sq, sq)
          pygame.draw.rect(self.screen, black, square)
    self.sprite.draw(self.screen)
    pygame.display.flip()

  def game_loop(self):
    while True:
      self.handle_events()
      self.move_sprite(self.sprite)
      self.draw()
      time.sleep(delay)

if __name__ == '__main__':
  pygame.init()
  game = TestGame()
  game.game_loop()
