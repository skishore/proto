# The number of words shown in each frame when text is animated.
word_speed = 1

# The number of frames used to animate a Pokemon fainting.
frames = 2
delay = 6

# The number of flashes and the number of frames for each one.
rounds = 2
period = 2


class AnimateMenu(object):
  def __init__(self, menu, speed=word_speed):
    self.menu = menu
    self.speed = speed
    self.length = len(' '.join(menu).split())
    self.index = 0

  def is_done(self):
    return self.index >= self.length

  def step(self):
    self.index += self.speed

  def update_display(self, display):
    new_menu = []
    index = self.index
    for line in self.menu:
      words = line.split()
      new_menu.append(' '.join(words[:index]))
      index -= len(words)
      if index <= 0:
        break
    display['menu'] = new_menu


class FaintPokemon(object):
  def __init__(self, target_id, length=frames, delay=delay, menu=None):
    self.target_id = target_id
    self.length = length
    self.delay = delay
    self.index = 0
    self.menu = menu

  def is_done(self):
    return self.index >= self.length + self.delay

  def step(self):
    self.index += 1

  def update_display(self, display):
    height = min(float(self.index)/self.length, 1)
    if 'height_offsets' not in display:
      display['height_offsets'] = {}
    display['height_offsets'][self.target_id] = height
    if self.menu:
      display['menu'] = self.menu


class FlashPokemon(object):
  def __init__(self, target_id, rounds=rounds, period=period):
    self.target_id = target_id
    self.length = 2*rounds*period
    self.period = period
    self.index = 0

  def is_done(self):
    return self.index >= self.length

  def step(self):
    self.index += 1

  def update_display(self, display):
    if (self.index / self.period) % 2:
      if 'hidden_indices' not in display:
        display['hidden_indices'] = set()
      display['hidden_indices'].add(self.target_id)
