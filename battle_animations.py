text_speed = 8


class AnimateMenu(object):
  def __init__(self, menu, speed=text_speed):
    self.menu = menu
    self.speed = speed
    self.length = sum(len(line) for line in menu)
    self.index = 0

  def is_done(self):
    return self.index >= self.length

  def step(self):
    self.index += self.speed

  def update_display(self, display):
    new_menu = []
    index = self.index
    for line in self.menu:
      new_menu.append(line[:index])
      index -= len(line)
      if index <= 0:
        break
    display['menu'] = new_menu
