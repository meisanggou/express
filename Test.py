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
# response = requests.post("http://127.0.0.1:1191/explain/", data=json.dumps({"content": u"申通 229357549351 电池", "openid": "oFBQiwq5QlIBtUTsr2tuMIFnSORs"}))
# print(response.text)

explain_success = u"***恭喜您***\n 您提供的%s公司运单号为%s备注为%s的快递可以监听,监听密钥：%s。" \
                               u"请直接复制本条消息回复，即可开始监听。"

content = explain_success % (u"申通快递", "229357549351", "", "b3bc463c5a8011e5b4ab50af736dfb82")
print(content)
regex = explain_success[10:] % (u'[a-zA-Z\u4e00-\u9fa5]+?', "[0-9]{10,12}", "[\s\S]*?", "([a-z0-9]{32})")
print(regex)
keys = re.findall(regex, content)
if len(keys) != 1:
    print content
print(keys)

