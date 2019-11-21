# encoding:utf-8


def override_str(clz):
  def __str__(self):
    return '%s[%s]' % (
      type(self).__name__,  # class name
      ', '.join('%s: %s' % item for item in vars(self).items())
    )

  clz.__str__ = __str__
  return clz
