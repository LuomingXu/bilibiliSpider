import multi_danmaku
import online
import user

if __name__ == '__main__':
  aid_mid = online.__main__()  # online
  user.__main__(aid_mid[1])  # owner
  multi_danmaku.main(aid_mid[0])  # multi danmaku
  # danmaku.__main__()  # danmaku
  print('done')
