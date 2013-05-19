import math
import pygame
from pygame.rect import Rect


ZERO = 0.001


class Sprite(object):
  def __init__(self, sq, square, color):
    self.sq = sq
    self.pos = (sq*square[0], sq*square[1])
    self.rect = Rect(self.pos[0], self.pos[1], self.sq, self.sq)
    self.velocity = (0, 0)
    self.color = color

  def cur_square(self):
    return (
      int(math.floor(1.0*self.pos[0]/self.sq + 0.5)),
      int(math.floor(1.0*self.pos[1]/self.sq + 0.5)),
    )

  def handle_blocks(self, is_square_blocked, tolerance, pushaway):
    if not any(self.velocity):
      return

    collided = False
    offset = [0, 0]
    square = self.cur_square()

    magnitude = self.magnitude()

    # Check if we cross a vertical square boundary and adjust the y-velocity.
    if abs(self.velocity[1]) < ZERO:
      offset[1] = 0
    elif self.velocity[1] < -((self.pos[1] + tolerance) % self.sq) + ZERO:
      offset[1] = -1
    elif self.velocity[1] > -self.pos[1] % self.sq - ZERO:
      offset[1] = 1

    if offset[1]:
      overlap = self.pos[0] - self.sq*square[0]
      offset[0] = 1 if overlap > 0 else -1
      if is_square_blocked((square[0], square[1] + offset[1])):
        collided = True
      elif abs(overlap) > tolerance:
        if is_square_blocked((square[0] + offset[0], square[1] + offset[1])):
          collided = True
          if abs(overlap) < pushaway and offset[0]*self.velocity[0] <= 0:
            speed = min(magnitude, abs(overlap) - tolerance)
            self.velocity[0] = -offset[0]*(speed + ZERO)

      if collided:
        if self.velocity[1] < 0:
          self.velocity[1] = -((self.pos[1] + tolerance) % self.sq) + ZERO
        else:
          self.velocity[1] = -self.pos[1] % self.sq - ZERO

    # Similar checks for horizontal square boundaries.
    offset[0] = 0
    if abs(self.velocity[0]) < ZERO:
      offset[0] = 0
    elif self.velocity[0] < -((self.pos[0] + tolerance) % self.sq) + ZERO:
      offset[0] = -1
    elif self.velocity[0] > (-self.pos[0] + tolerance) % self.sq - ZERO:
      offset[0] = 1

    if offset[0]:
      overlap = self.pos[1] - self.sq*square[1]
      collided = (
        offset[1] and not collided and
        is_square_blocked((square[0] + offset[0], square[1] + offset[1]))
      )
      offset[1] = 1 if overlap > 0 else -1
      if is_square_blocked((square[0] + offset[0], square[1])):
        collided = True
      elif overlap > 0 or -overlap > tolerance:
        if is_square_blocked((square[0] + offset[0], square[1] + offset[1])):
          collided = True
          if abs(overlap) < pushaway and offset[1]*self.velocity[1] <= 0:
            is_blocked = is_square_blocked((square[0], square[1] + offset[1]))
            speed = min(magnitude, overlap if overlap > 0 else -(overlap + tolerance))
            self.velocity[1] = 0 if is_blocked else -offset[1]*(speed + ZERO)

      if collided:
        if self.velocity[0] < 0:
          self.velocity[0] = -((self.pos[0] + tolerance) % self.sq) + ZERO
        else:
          self.velocity[0] = (-self.pos[0] + tolerance) % self.sq - ZERO

  def magnitude(self):
    return math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

  def move(self):
    if any(self.velocity):
      self.pos = (self.pos[0] + self.velocity[0], self.pos[1] + self.velocity[1])
      self.rect = Rect(self.pos[0] + 0.5 - ZERO, self.pos[1] + 0.5 - ZERO, self.sq, self.sq)

  def normalize(self, speed):
    magnitude = self.magnitude()
    if magnitude > speed:
      self.velocity = [float(speed)/magnitude*v for v in self.velocity]

  def draw(self, screen):
    pygame.draw.rect(screen, self.color, self.rect)
