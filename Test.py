#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'

import requests
import re
from Service.Express_Query import ExpressQuery
from Service.Express_DB import ExpressDB
import json

eq = ExpressQuery()
eDB = ExpressDB()


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

# kd100_info = eq.kd100("yuantong", "200246227212 ")
# print(kd100_info["status_code"])
# for kdi in kd100_info["express_info"]:
#     print(kdi["time"])
#     print(kdi["info"])

from Service.User_DB import UserDB
# response = requests.post("http://localhost:1191/explain/", data=json.dumps({"content": "zto,229357549351", "openid": "oFBQiwq5QlIBtUTsr2tuMIFnSORs"}))
# print(response.text)
# result = eDB.select_pre_listen("a86864cf59d811e587a5ac72893dafe9", "meisanggou")
# query_result = result["query_result"]
# infos = json.loads(query_result)
# for info in infos:
#     print(info["info"])

explain_success = u"***恭喜您*** 您提供的%s公司运单号为%s快递可以监听,监听密钥:%s。请直接复制本条消息回复，即可开始监听。"
content = explain_success % ("zto", "229357549351", "a86864cf59d811e587a5ac72893dafe9")
print(content)

regex = explain_success[10:] % ("[a-z]+", "[0-9]{10,12}", "([a-z0-9]{32})")
print(regex)

result = re.findall(regex, content)
print(result)
