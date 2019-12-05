import danmaku
import online
import user

if __name__ == '__main__':
  # online
  cid_mid = online.__main__()
  # owner
  user.__main__(cid_mid[1])
  # danmaku
  danmaku.__main__()
  print('done')
