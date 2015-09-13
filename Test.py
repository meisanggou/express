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


def yto(waybillNo):
    """
    圆通速递
    :return:
    """
    url = "http://trace.yto.net.cn:8022/TraceSimple.aspx"
    data = "waybillNo=%s&validateCode=" % waybillNo
    print(data)
    heads = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=heads)
    # print(requests)
    print(response.text)
    return "true"
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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

kd100_info = eq.query("zto", "762852300291")

url = "http://m.kuaidi100.com/index_all.html?type=zhongtong&postid=762852300291"
response = requests.get(url)
print(response.text)
