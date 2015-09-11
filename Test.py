#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'

import requests
import re


sto_status = ("收件员收件", "快件运输中", "正在派件", "已签收")


def sto(wen):
    """
    申通快递
    :param wen:
    :return:
    """
    url = "http://q.sto.cn/track.aspx?wen=%s" % wen
    response = requests.get(url)
    r_text = response.text
    status = re.findall('<span id="Repeater1_lblTime[1-4]_0">([\s\S]*?)</span>', r_text)
    status_code = len(status)
    for i in range(len(sto_status)):
        if status[i] == "":
            status_code = i
            break
    tab_result = re.search('<table cellpadding="0" cellspacing="0" class="tab_result" width="100%">[\s\S]*?</table>', r_text).group()
    record_tr = re.findall('<tr>([\s\S]*?)<\/tr>', tab_result)
    express_info = []
    for tr in record_tr:
        record_td = re.findall('<td width="[27]5%">([ \S]*?)<\/td>', tr)
        time = record_td[0]
        temp_info = record_td[1]
        info = "".join(re.split('</?a[ \S]*?>', temp_info))
        express_info.append({"time": time, "info": info})
    sto_info = {"express_info": express_info, "status_code": status_code}
    return sto_info
sto_info = sto("229357549351")
print(sto_info["status_code"])
for ei in sto_info["express_info"]:
    print("%s %s" % (ei["time"], ei["info"]))


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
# 中通 762821834691

# zto 中通
response = requests.get("http://www.zto.cn/GuestService/Bill?txtbill=762821834691")
print(response.text)