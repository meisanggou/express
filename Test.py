#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'

import requests
import re
from Service.Express_Query import ExpressQuery
from Service.Express_DB import ExpressDB
import json
from Tools.Wx import WxManager

eq = ExpressQuery()
eDB = ExpressDB()
wx = WxManager()


# yto_info = yto("200246227212")
# print(yto_info)

# 韵达 1600822332578
# 天天 550184678493

# zto 中通
# 在途 762862300291 762863500291
# 完成 762852300291 762821834691
# billcode = "762852300291"
# zto_info = eq.zto(billcode)
# print(zto_info["status_code"])
# for zi in zto_info["express_info"]:
#     print(zi["time"])
#     print(zi["info"])
response = requests.get("http://127.0.0.1:1191/mine/", data=json.dumps({"content": u"申通,229255098587", "openid": "oFBQiwq5QlIBtUTsr2tuMIFnSORs"}))
print(response.text)
