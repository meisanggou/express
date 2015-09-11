# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

import re
import requests


class ExpressQuery:

    def __init__(self):
        # print("Init Success")
        self.sto_status = ("收件员收件", "快件运输中", "正在派件", "已签收")

    def sto(self, wen):
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
        for i in range(len(self.sto_status)):
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

    def zto(self, billcode):
        """
        中通快递
        :param billcode:
        :return:
        """
        response = requests.get("http://www.zto.cn/GuestService/Bill?txtbill=%s" % billcode)
        r_text = response.text
        state_result = re.search('<div class="state">[\s\S]*?<ul>[\s\S]*?</ul>[\s\S]*?</div>', r_text)
        if state_result is None:
            return {"express_info": [], "status_code": 0}
        state = state_result.group()
        record_li = re.findall('<li class="pr ([\s\S]*?)</li>', state)
        status_key = '<div data-billcode="%s"' % billcode
        index = record_li[0].find(status_key)
        if index >= 0:
            status_code = 4
            record_li[0] = record_li[0][index + 1:]
        else:
            status_code = 2
        express_info = []
        for li in record_li:
            recode_div = re.findall('<div[^>]*?>([\s\S]*?)</div>', li)
            temp_info = recode_div[0]
            time = recode_div[1]
            info = "".join(re.split('</?a[ \S]*?>', temp_info))
            express_info.append({"time": time, "info": info})
        zto_info = {"express_info": express_info, "status_code": status_code}
        return zto_info
