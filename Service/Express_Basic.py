# encoding: utf-8
# !/usr/bin/python

import re
import uuid
from Express_Query import ExpressQuery
__author__ = 'zhouheng'


class ExpressBasic:

    def __init__(self):
        self.express_com = {"sto": "申通快递", "zto": "中通快递", "tiantian": "天天快递", "yuantong": "圆通速递"}
        self.eq = ExpressQuery()

    def check_waybill(self, com, waybill):
        if com not in self.express_com.keys():
            return False, u"不支持的快递", []
        if len(waybill) > 12 or len(waybill) < 10:
            return False, u"运单号不正确", []
        search_result = re.search('[^0-9]', waybill)
        if search_result is not None:
            return False, u"运单号不正确", []
        result = self.eq.query(com, waybill)
        if result["status_code"] == 0:
            return False, u"未查到相关快递信息", []
        if result["completed"] is True:
            return False, u"运单已签收", []
        no = uuid.uuid1().hex
        return True, no, result["express_info"]


