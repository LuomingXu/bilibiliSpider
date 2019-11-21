# encoding:UTF-8
import json
import sys
import time
from typing import List

import res
from Bilibili import UserProfile
from BilibiliDO import UserProfileDO
from db import DBSession


class ShowProcess:
  """
  显示处理进度的类
  调用该类相关函数即可实现处理进度的显示
  """
  i = 0  # 当前的处理进度
  max_steps = 0  # 总共需要处理的次数
  max_arrow = 50  # 进度条的长度
  infoDone = 'done'

  # 初始化函数，需要知道总共的处理次数
  def __init__(self, max_steps, infoDone = 'Done'):
    self.max_steps = max_steps
    self.i = 0
    self.infoDone = infoDone

  # 显示函数，根据当前的处理进度i显示进度
  # 效果为[>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]100.00%
  def show_process(self, i = None):
    if i is not None:
      self.i = i
    else:
      self.i += 1
    num_arrow = int(self.i * self.max_arrow / self.max_steps)  # 计算显示多少个'>'
    num_line = self.max_arrow - num_arrow  # 计算显示多少个'-'
    percent = self.i * 100.0 / self.max_steps  # 计算完成进度，格式为xx.xx%
    process_bar = '[' + '>' * num_arrow + '-' * num_line + ']' \
                  + '%.2f' % percent + '%' + '\r'  # 带输出的字符串，'\r'表示不换行回到最左边
    sys.stdout.write(process_bar)  # 这两句打印字符到终端
    sys.stdout.flush()
    if self.i >= self.max_steps:
      self.close()

  def close(self):
    print('')
    print(self.infoDone)
    self.i = 0


if __name__ == '__main__':
  max = 10000
  process_bar = ShowProcess(max, 'Done')
  session = DBSession()

  http = res.Request()
  DOs: List[UserProfileDO] = []
  for i in range(1, max):
    mid = {'mid': i}
    http.get('https://api.bilibili.com/x/space/acc/info', **mid)

    try:
      resData = json.loads(http.res.data, object_hook = UserProfile.from_dict)
      DOs.append(UserProfileDO(resData))
    except Exception:
      print(mid)
      print(http.res.data)

    try:
      if i % 50 == 0:
        session.bulk_save_objects(DOs)
        session.commit()
        print('i: %s. insert success.' % i)
    except Exception:
      print(i)
      print(DOs.__len__())

    process_bar.show_process()
    time.sleep(0.05)

# role = Role(1, 'test_role')
# test = user.User('xjy', '')
#
# for item in vars(test).items():
#   print(item)

# session = DBSession()
# # 创建新User对象:
# role = Role(1, 'test_role')
# # 添加到session:
# session.add(role)
# # 提交即保存到数据库:
# session.commit()
# # 关闭session:
# session.close()

# query: List[Role] = session.query(Role).filter(Role.role_name == 'admin').all()
#
# for item in query:
#   print(item)

# e = res.Request()
# test = user.User('xjy', '')
#
# print(urlencode(test.__dict__))
# dict = {"userName": "xjy", "password": "xjy"}
#
# e.put('http:\\\\localhost:8080\\user\\role\\26580838456102913\\26585030654562358')
# print(e.res.data)
#
# u = user.User('syun', 'syun', 'syun@syun.com')
# print(json.dumps(u.__dict__))
