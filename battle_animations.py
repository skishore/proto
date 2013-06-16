word_speed = 1


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
