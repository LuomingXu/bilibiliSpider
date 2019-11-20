# encoding:UTF-8
import res
import user
import json
from urllib.parse import urlencode

e = res.Request()
test = user.User('xjy', '')

print(urlencode(test.__dict__))
dict = {"userName": "xjy", "password": "xjy"}

e.put('http://localhost:8080/user/role/26580838456102913/26585030654562358')
print(e.res.data)

u = user.User('syun', 'syun', 'syun@syun.com')
print(json.dumps(u.__dict__))
