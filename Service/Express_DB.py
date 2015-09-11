# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Tools.Mysql_db import DB


class ExpressDB:

    def __init__(self):
        self.db = DB()
        self.db.connect()
        self.completed_express = "completed_express"
        self.transport_express = "transport_express"
        self.listen_express = "listen_express"
        self.completed_express_desc = self.transport_express_desc = [
            ["recode_no", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["sign_time", "datetime", "NO", "", None, ""],
            ["sign_info", "varchar(50)", "NO", "", None, ""],
        ]
        self.listen_express_desc = [
            ["listen_no", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["update_time", "datetime", "NO", "", None, ""],
            ["check_time", "datetime", "NO", "", None, ""],
        ]

    def create_completed_express(self, force=False):
        return self.db.create_table(self.completed_express, self.completed_express_desc, force)

    def check_completed_express(self):
        return self.db.check_table(self.completed_express, self.completed_express_desc)

    def create_transport_express(self, force=False):
        return self.db.create_table(self.transport_express, self.transport_express_desc, force)

    def check_transport_express(self):
        return self.db.check_table(self.transport_express, self.transport_express_desc)

    def create_listen_express(self, force=False):
        return self.db.create_table(self.listen_express, self.listen_express_desc, force)

    def check_listen_express(self):
        return self.db.check_table(self.listen_express, self.listen_express_desc)