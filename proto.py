import pygame
import sys
import time

from battle import Battle
from key_repeater import KeyRepeater
from ui import (
  BattleUI,
  screen_size,
)

framerate = 24
delay = 1.0/framerate


class TestGame(object):
  def __init__(self):
    self.screen = pygame.display.set_mode(screen_size)
    self.key_repeater = self.construct_key_repeater()
    self.battle = Battle()
    self.ui = BattleUI()

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

  def game_loop(self):
    while True:
      if self.handle_events():
        self.draw()
      time.sleep(delay)

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
      self.key_repeater.handle_event(event)
    keys = self.key_repeater.query()
    if pygame.K_ESCAPE in keys:
      sys.exit()
    return self.battle.transition(keys)

  def draw(self):
    self.ui.draw(self.screen, self.battle)
    pygame.display.flip()

if __name__ == '__main__':
  pygame.init()
  game = TestGame()
  game.game_loop()
