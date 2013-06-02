import pygame
from pygame.rect import Rect

colorkey = (255, 192, 255)


class Sprite(object):
  image_memo = {}

  def __init__(self, filename, width, height, cols, rows, offset, period):
    if filename not in Sprite.image_memo:
      path = 'images/%s' % (filename,)
      Sprite.image_memo[filename] = pygame.image.load(path).convert()
    self.image = Sprite.image_memo[filename]
    self.image.set_colorkey(colorkey)
    self.rect = Rect(0, 0, width, height)
    self.width = width
    self.height = height
    self.cols = cols
    self.rows = rows
    self.offset = offset
    self.period = period
    self.set_index()

  def set_index(self, index=0):
    (col, row) = (index % self.cols, index / self.cols)
    self.source_rect = Rect(
      self.offset[0] + col*self.period[0],
      self.offset[1] + row*self.period[1],
      self.width,
      self.height,
    )

  def set_position(self, left, top):
    self.rect.left = left
    self.rect.top = top

  def draw(self, surface):
    surface.blit(self.image, self.rect, area=self.source_rect)
