# encoding: utf-8
# !/usr/bin/python

from datetime import datetime
from time import sleep

from Tools.Mysql_db import DB
from Service import TIME_FORMAT
from Express_Query import ExpressQuery

__author__ = 'zhouheng'


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
            ["sign_info", "varchar(50)", "NO", "", None, ""]
        ]
        self.listen_express_desc = [
            ["listen_no", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["update_time", "datetime", "NO", "", None, ""],
            ["query_time", "datetime", "NO", "", None, ""],
            ["call_email", "varchar(30)", "NO", "", None, ""]
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

    def new_express_record(self, com_code, waybill_num, recodes, completed=False):
        if len(recodes) <= 0:
            return True
        insert_sql = "INSERT INTO %s (com_code,waybill_num,sign_time,sign_info) VALUES " \
                     % (self.completed_express if completed is True else self.transport_express)
        for recode in recodes:
            insert_sql += "('%s','%s','%s','%s')," % (com_code, waybill_num, recode["time"], recode["info"])
        insert_sql = insert_sql[:-1] + ";"
        self.db.execute(insert_sql)
        return True

    def del_express_record(self, com_code, waybill_num):
        del_sql = "DELETE FROM %s WHERE com_code='%s' AND waybill_num='%s';" % (self.transport_express, com_code, waybill_num)
        self.db.execute(del_sql)
        return True

    def new_listen_record(self, com_code, waybill_num, call_email):
        now_time = datetime.now().strftime(TIME_FORMAT)
        insert_sql = "INSERT INTO %s (com_code, waybill_num,update_time,query_time,call_email) " \
                     "VALUES ('%s','%s','%s','%s','%s');" \
                     % (self.listen_express, com_code, waybill_num, now_time, now_time, call_email)
        self.db.execute(insert_sql)
        return True

    def update_listen_record(self, com_code, waybill_num, update=False, query=False):
        if update is False and query is False:
            return True
        update_sql = "UPDATE %s SET " % self.listen_express
        now_time = datetime.now().strftime(TIME_FORMAT)
        if update is True:
            update_sql += "update_time='%s'," % now_time
        if query is True:
            update_sql += "query_time='%s'," % now_time
        update_sql = update_sql[:-1] + " WHERE com_code='%s' AND waybill_num='%s';" % (com_code, waybill_num)
        print(update_sql)
        self.db.execute(update_sql)
        return True

    def del_listen_record(self, com_code, waybill_num):
        del_sql = "DELETE FROM %s WHERE com_code='%s' AND waybill_num='%s';" % (self.listen_express, com_code, waybill_num)
        self.db.execute(del_sql)
        return True

    def loop_query(self):
        eq = ExpressQuery()
        while True:
            # 睡眠5分钟
            print("Sleep 5 Minutes")
            sleep(30)
            # 最后最晚查询过的一条记录
            select_sql = "SELECT com_code,waybill_num,MIN(query_time),update_time,call_email FROM listen_express;"
            self.db.execute(select_sql)
            record = self.db.fetchone()
            if record[0] is None:
                print("No Listen Record")
                continue
            com_code = record[0]
            waybill_num = record[1]
            update_time = record[3]
            call_email = record[4]
            print("Start Handle %s %s" % (com_code, waybill_num))
            # 查询现在快速状态
            query_result = eq.query(com_code, waybill_num)
            if query_result["completed"] is True:
                print("%s %s completed" % (com_code, waybill_num))
                # 通知用户完成
                # 删除transport_express中对应的记录
                self.del_express_record(com_code, waybill_num)
                # 删除listen_express中对应的记录
                self.del_listen_record(com_code, waybill_num)
                # 将全部记录记入completed_express
                self.new_express_record(com_code, waybill_num, query_result["express_info"], True)
                continue
            # 查询数据库中已有记录进行比对
            select_sql = "SELECT COUNT(com_code) FROM transport_express WHERE com_code='%s' AND waybill_num='%s';" % (com_code, waybill_num)
            self.db.execute(select_sql)
            recode_num = self.db.fetchone()[0]
            if recode_num == len(query_result["express_info"]):
                # 没有更新的快递信息
                # 判断是否超过5天没有更新记录
                if (datetime.now() - update_time).days >= 5:
                    print("Long time no info")
                    # 通知用户
                    # 删除transport_express中对应的记录
                    self.del_express_record(com_code, waybill_num)
                    # 删除listen_express中对应的记录
                    self.del_listen_record(com_code, waybill_num)
                else:
                    # 更新 query_time
                    self.update_listen_record(com_code, waybill_num, False, True)
            else:
                print("%s %s has new info." % (com_code, waybill_num))
                # 通知用户

                # 添加运输记录
                add_record = []
                for index in range(recode_num, len(query_result["express_info"])):
                    add_record.append(query_result["express_info"][index])
                self.new_express_record(com_code, waybill_num, add_record, False)
                # 更新update_time query_time
                self.update_listen_record(com_code, waybill_num, True, True)
