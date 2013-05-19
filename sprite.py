import math
import pygame
from pygame.rect import Rect


class Sprite(object):
  def __init__(self, sq, square, color):
    self.sq = sq
    self.rect = Rect(sq*square[0], sq*square[1], sq, sq)
    self.velocity = (0, 0)
    self.color = color

  def cur_square(self):
    return (
      int(math.floor(1.0*self.rect.left/self.sq + 0.5)),
      int(math.floor(1.0*self.rect.top/self.sq + 0.5)),
    )

  def handle_blocks(self, is_square_blocked, tolerance, pushaway):
    if not any(self.velocity):
      return

    collided = False
    offset = (0, 0)
    pos = (self.rect.left, self.rect.top)
    square = self.cur_square()

    magnitude = self.magnitude()

    # Check if we cross a vertical square boundary and adjust the y-velocity.
    if self.velocity[1] < -((pos[1] + tolerance) % self.sq):
      offset[1] = -1
    elif self.velocity[1] > -pos[1] % self.sq:
      offset[1] = 1

    if offset[1]:
      overlap = pos[0] - self.sq*square[0]
      offset[0] = 1 if overlap > 0 else -1
      if is_square_blocked((square[0], square[1] + offset[1])):
        collided = True
      elif abs(overlap) > tolerance:
        if is_square_blocked((square[0] + offset[0], square[1] + offset[1])):
          collided = True
          if abs(overlap) < pushaway and offset[0]*self.velocity[0] <= 0:
            self.velocity[0] = -offset[0]*magnitude

      if collided:
        if self.velocity[1] < 0:
          self.velocity[1] = -((pos[1] + tolerance) % self.sq)
        else:
          self.velocity[1] = -pos[1] % self.sq

    # Similar checks for horizontal square boundaries.
    offset[0] = 0
    if self.velocity[0] < -((pos[0] + tolerance) % self.sq):
      offset[0] = -1
    elif self.velocity[1] > (-pos[0] + tolerance) % self.sq:
      offset[1] = 1

    if offset[0]:
      overlap = pos[1] - self.sq*square[1]
      collided = (
        offset[1] and not collided and
        is_square_blocked((square[0] + offset[0], square[1] + offset[1]))
      )
      offset[1] = 1 if overlap > 0 else -1
      if is_square_blocked((square[0] + offset[0], square[1])):
        collided = True
      elif offset[1] > 0 or -overlap > tolerance:
        if is_square_blocked((square[0] + offset[0], square[1] + offset[1])):
          collided = True
          if abs(overlap) < pushaway and offset[1]*self.velocity[1] <= 0:
            is_blocked = is_square_blocked((square[0], square[1] + offset[1]))
            self.velocity[1] = 0 if is_blocked else -offset[1]*magnitude

      if collided:
        if self.velocity[0] < 0:
          self.velocity[0] = -((pos[0] + tolerance) % self.sq)
        else:
          self.velocity[0] = (-pos[0] + tolerance) % self.sq

  def magnitude(self):
    return math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

  def move(self):
    self.rect = self.rect.move(self.velocity)

  def normalize(self, speed):
    magnitude = self.magnitude()
    if magnitude > speed:
      self.velocity = tuple(float(speed)/magnitude*v for v in self.velocity)

  def draw(self, screen):
    pygame.draw.rect(screen, self.color, self.rect)
