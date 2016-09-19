# encoding: utf-8
# !/usr/bin/python

import re
import uuid
from Express_Query import ExpressQuery
__author__ = 'zhouheng'


class ExpressBasic:

    def __init__(self):
        self.eq = ExpressQuery()

    def check_waybill(self, com, waybill):
        if len(waybill) > 20 or len(waybill) < 10:
            return False, u"运单号不正确", []
        no = uuid.uuid1().hex
        search_result = re.search('[^0-9]', waybill)
        if search_result is not None:
            return False, u"运单号应为纯数字", []
        result = self.eq.query(com, waybill)
        if result["status_code"] == 0:
            return True, no, []
        if result["completed"] is True:
            return False, u"运单已签收", []
        return True, no, result["express_info"]
