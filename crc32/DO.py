class crc32DO(object):

  def __init__(self, hash: int, value: int):
    self.hash = hash
    self.value = value

  def __str__(self):
    return '(%s, %s)' % (self.hash, self.value)
