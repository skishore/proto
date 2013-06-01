from data import johto_to_kanto_map


assert(set(johto_to_kanto_map.iterkeys()) == set(xrange(1, 252)))
assert(set(johto_to_kanto_map.itervalues()) == set(xrange(1, 252)))
kanto_to_johto_map = dict(
  (kanto, johto) for (johto, kanto) in johto_to_kanto_map.iteritems()
)


def get_front_index(pokenum):
  result = kanto_to_johto_map[pokenum]
  # Account for the fact that we have an extra Jynx sprite.
  if result > 153:
    result += 1
  return result - 1
