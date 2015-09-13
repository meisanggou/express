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

kd100_info = eq.query("zto", "762852300291")


kd100_info["express_info"] = kd100_info["express_info"][0:1]
recodes = []
len_info = len(kd100_info["express_info"])
for index in range(0, 3):
    if 3 - index > len_info:
        recodes.append({"time": "", "info": ""})
        continue
    recodes.append(kd100_info["express_info"][len_info + index - 3])
print(recodes)


from Service.User_DB import UserDB
# response = requests.post("http://localhost:1191/add/", data=json.dumps({"listen_key": "e331f07059df11e5b54300163e0045ef", "openid": "oFBQiwq5QlIBtUTsr2tuMIFnSORs"}))
# print(response.text)
# result = eDB.select_pre_listen("a86864cf59d811e587a5ac72893dafe9", "meisanggou")
# query_result = result["query_result"]
# infos = json.loads(query_result)
# for info in infos:
#     print(info["info"])



# recodes = [{"time": "2015-09-13 14:46:48", "info": "testvdfs"}, {"time": "2015-09-13 14:46:48", "info": "testvdfs"}, {"time": "2015-09-13 14:46:48", "info": "testvdfs"}]
# result = wx.send_express_template("meisanggou", "oFBQiwq5QlIBtUTsr2tuMIFnSORs", "exception", "zto", "200246227212", "zanwu", recodes)
# print(result)