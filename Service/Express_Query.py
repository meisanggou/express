# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

import re
import requests
import json
import random


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
        completed = False
        for i in range(len(self.sto_status)):
            if status[i] == "":
                status_code = i
                break
        if status_code == len(status):
            completed = True
        tab_result = re.search('<table cellpadding="0" cellspacing="0" class="tab_result" width="100%">[\s\S]*?</table>', r_text).group()
        record_tr = re.findall('<tr>([\s\S]*?)<\/tr>', tab_result)
        express_info = []
        for tr in record_tr:
            record_td = re.findall('<td width="[27]5%">([ \S]*?)<\/td>', tr)
            time = record_td[0].replace("/", "-")
            temp_info = record_td[1]
            info = "".join(re.split('</?a[ \S]*?>', temp_info))
            express_info.append({"time": time, "info": info})
        sto_info = {"express_info": express_info, "status_code": status_code, "completed": completed}
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
        completed = False
        if index >= 0:
            status_code = 4
            record_li[0] = record_li[0][index + 1:]
            completed = True
        else:
            status_code = 2
        express_info = []
        len_li = len(record_li)
        for index in range(len_li):
            li = record_li[len_li - index - 1]
            recode_div = re.findall('<div[^>]*?>([\s\S]*?)</div>', li)
            temp_info = recode_div[0]
            time = recode_div[1]
            info = "".join(re.split('</?a[ \S]*?>', temp_info))
            express_info.append({"time": time, "info": info})
        zto_info = {"express_info": express_info, "status_code": status_code, "completed": completed}
        return zto_info

    def zhaijisong(self, orderNos):
        url = "http://www.zjs.com.cn/api/tracking.jspx"
        data = "orderNos=%s" % orderNos
        response = requests.post(url, data=data)
        print(response.text)
        return "true"

    def kd100(self, comCode, wayBill):
        temp = random.random()
        s = requests.session()
        url = "http://www.kuaidi100.com/query?type=%s&postid=%s&id=1&valicode=&temp=%s" % (comCode, wayBill, temp)
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"}
        headers["Referer"] = "http://www.kuaidi100.com/"
        headers["X-Requested-With"] = "XMLHttpRequest"
        response = s.get(url, headers=headers)
        content = response.content.decode("utf-8")
        result = json.loads(content)
        express_info = []
        status_code = 0
        completed = False
        if result["message"] == "ok":
            status_code = int(result["state"]) + 1
            if status_code == 4:
                completed = True
            records = result["data"]
            record_len = len(records)
            for index in range(record_len):
                record = records[record_len-index-1]
                express_info.append({"time": record["ftime"], "info": record["context"]})
        kd100_info = {"express_info": express_info, "status_code": status_code, "completed": completed}
        return kd100_info

    def query(self, comCode, wayBill):
        return self.kd100(comCode, wayBill)
        # if comCode == "shentong":
        #     return self.sto(wayBill)
        if comCode == "zhongtong":
            return self.zto(wayBill)
        else:
            return self.kd100(comCode, wayBill)
