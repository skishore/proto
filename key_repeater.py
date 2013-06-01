import pygame


class KeyRepeater(object):
  def __init__(self, one_time_keys, repeated_keys, pause, repeat):
    self.keys = set(one_time_keys + repeated_keys)
    self.repeated_keys = set(repeated_keys)
    self.keys_held = set()
    self.fire_frames = dict((key, -1) for key in self.keys)
    self.pause = pause
    self.repeat = repeat

  def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key in self.keys:
        self.keys_held.add(event.key)
    elif event.type == pygame.KEYUP:
      if event.key in self.keys:
        self.keys_held.discard(event.key)
        if self.fire_frames[event.key] < 0:
          self.fire_frames[event.key] = 0
        else:
          self.fire_frames[event.key] = -1

  def query(self):
    result = set()
    for key in self.keys:
      if key in self.keys_held:
        if self.fire_frames[key] < 0:
          result.add(key)
          self.fire_frames[key] = self.pause
        elif self.fire_frames[key] == 0:
          if key in self.repeated_keys:
            result.add(key)
          self.fire_frames[key] = self.repeat
        else:
          self.fire_frames[key] -= 1
      elif self.fire_frames[key] == 0:
        result.add(key)
        self.fire_frames[key] = -1
    return result
