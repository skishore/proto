# The number of words shown in each frame when text is animated.
word_speed = 1

# The number of flashes and the number of frames for each one.
rounds = 2
frequency = 4


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


class FlashPokemon(object):
  def __init__(self, target_id, rounds=rounds, frequency=frequency):
    self.target_id = target_id
    self.length = 2*rounds*frequency
    self.frequency = frequency
    self.index = 0

  def is_done(self):
    return self.index >= self.length

  def step(self):
    self.index += 1

  def update_display(self, display):
    if (self.index / self.frequency) % 2:
      if 'hidden_indices' not in display:
        display['hidden_indices'] = set()
      display['hidden_indices'].add(self.target_id)
