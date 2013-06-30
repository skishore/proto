def oxford_list(words):
  assert(words)
  if len(words) == 1:
    return words[0]
  if len(words) == 2:
    return '%s and %s' % tuple(words)
  return ', '.join(words[:-1]) + ', and ' + words[-1]
