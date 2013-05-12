import pygame

class KeyRepeater(object):
  def __init__(self, one_time_keys, repeated_keys):
    self.keys = set(one_time_keys + repeated_keys)
    self.repeated_keys = set(repeated_keys)
    self.keys_held = set()
    self.keys_fired = set()

  def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key in self.keys:
        self.keys_held.add(event.key)
    elif event.type == pygame.KEYUP:
      if event.key in self.keys:
        self.keys_held.discard(event.key)
        self.keys_fired.discard(event.key)

  def query(self):
    result = set(
      key for key in self.keys_held
      if key in self.repeated_keys or key not in self.keys_fired
    )
    self.keys_fired.update(result)
    return result
