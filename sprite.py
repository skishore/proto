import math
import pygame
from pygame.rect import Rect

class Sprite(object):
  def __init__(self, sq, square, color):
    self.sq = sq
    self.rect = Rect(sq*square[0], sq*square[1], sq, sq)
    self.velocity = (0, 0)
    self.color = color

  def move(self):
    self.rect = self.rect.move(self.velocity)

  def normalize(self, speed):
    magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
    if magnitude > speed:
      self.velocity = tuple(float(speed)/magnitude*v for v in self.velocity)

  def draw(self, screen):
    pygame.draw.rect(screen, self.color, self.rect)
