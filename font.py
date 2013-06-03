import string

from sprite import Sprite

font = "%s():;[]%s%s'@#-?!.&~~>~~~/,~%s~~~~ " % (
  string.uppercase,
  string.lowercase,
  22*'~',
  string.digits,
)
assert(len(font) == 16*7)
font_pairs = [(char, i) for (i, char) in enumerate(font) if char != '~']
font_map = dict(font_pairs)
assert(len(font_map) == len(font_pairs))


class Font(Sprite):
  def __init__(self):
    super(Font, self).__init__(
      'text.bmp',
      width=8,
      height=8,
      cols=16,
      rows=7,
      offset=(19, 248),
      period=(8, 8),
    )

  def draw(self, surface, text, x, y):
    cur_x = x
    for char in text:
      if char in font_map:
        self.set_index(font_map[char])
        self.set_position(cur_x, y)
        if char != ' ':
          super(Font, self).draw(surface)
        cur_x += self.width
