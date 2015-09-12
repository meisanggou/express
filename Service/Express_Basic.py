# encoding: utf-8
# !/usr/bin/python

import re

__author__ = 'zhouheng'

class ExpressBasic:

    def __init__(self):
        self.express_com = {"sto": "申通快递", "zto": "中通快递"}

    def check_waybill(self, com, waybill):
        if com not in self.express_com.keys():
            return False
        if len(waybill) > 12 or len(waybill) < 10:
            return False
        search_result = re.search('[^0-9]', waybill)
        if search_result is not None:
            return False
        return True