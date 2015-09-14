# encoding: utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from datetime import datetime
from time import sleep

from Tools.Mysql_db import DB
from Service import TIME_FORMAT
from Express_Query import ExpressQuery
from Tools.Wx import WxManager
from User_DB import UserDB

__author__ = 'zhouheng'


class ExpressDB:

    def __init__(self):
        self.db = DB()
        self.db.connect()
        self.wx = WxManager()
        self.uDB = UserDB()
        self.completed_express = "completed_express"
        self.transport_express = "transport_express"
        self.listen_express = "listen_express"
        self.pre_listen = "pre_listen"
        self.express_com = "express_com"
        self.completed_express_desc = self.transport_express_desc = [
            ["recode_no", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["sign_time", "datetime", "NO", "", None, ""],
            ["sign_info", "varchar(150)", "NO", "", None, ""],
            ["user", "varchar(30)", "NO", "", None, ""]
        ]
        self.listen_express_desc = [
            ["listen_no", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["remark", "varchar(10)", "NO", "", None, ""],
            ["update_time", "datetime", "NO", "", None, ""],
            ["query_time", "datetime", "NO", "", None, ""],
            ["user", "varchar(30)", "NO", "", None, ""]
        ]
        self.pre_listen_desc = [
            ["listen_key", "char(32)", "NO", "PRI", None, ""],
            ["com_code", "varchar(10)", "NO", "", None, ""],
            ["waybill_num", "varchar(20)", "NO", "", None, ""],
            ["remark", "varchar(10)", "NO", "", None, ""],
            ["insert_time", "datetime", "NO", "", None, ""],
            ["query_result", "varchar(1000)", "NO", "", None, ""],
            ["user_no", "int(11)", "NO", "", None, ""]
        ]
        self.express_com_desc = [
            ["com_code", "varchar(30)", "NO", "PRI", None, ""],
            ["com_name", "varchar(20)", "NO", "", None, ""]
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

    def create_pre_listen(self, force=False):
        return self.db.create_table(self.pre_listen, self.pre_listen_desc, force)

    def check_pre_listen(self):
        return self.db.check_table(self.pre_listen, self.pre_listen_desc)

    def create_express_com(self, force=False):
        return self.db.create_table(self.express_com, self.express_com_desc, force)

    def check_express_com(self):
        return self.db.check_table(self.express_com, self.express_com_desc)

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

    def new_listen_record(self, com_code, waybill_num, remark, user):
        now_time = datetime.now().strftime(TIME_FORMAT)
        insert_sql = "INSERT INTO %s (com_code, waybill_num,update_time,query_time,remark,user) " \
                     "VALUES ('%s','%s','%s','%s','%s', '%s');" \
                     % (self.listen_express, com_code, waybill_num, now_time, now_time, remark, user)
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
        self.db.execute(update_sql)
        return True

    def del_listen_record(self, com_code, waybill_num):
        del_sql = "DELETE FROM %s WHERE com_code='%s' AND waybill_num='%s';" % (self.listen_express, com_code, waybill_num)
        self.db.execute(del_sql)
        return True

    def select_listen_record(self, user):
        select_sql = "SELECT l.com_code,waybill_num,remark,com_name FROM %s AS l,%s AS c WHERE user='%s' " \
                     "AND l.com_code=c.com_code;" % (self.listen_express, self.express_com, user)
        result = self.db.execute(select_sql)
        listen_info = []
        for item in self.db.fetchall():
            listen_info.append({"com_code": item[0], "waybill_num": item[1], "remark": item[2], "com_name": item[3]})
        return listen_info

    def new_pre_listen(self, listen_key, com_code, waybill_num, remark, user_no, query_result):
        try:
            now_time = datetime.now().strftime(TIME_FORMAT)
            query_result = self.db.format_string(query_result)
            insert_sql = "INSERT INTO %s (listen_key,com_code,waybill_num,insert_time,query_result,remark,user_no) " \
                         "VALUES ('%s','%s','%s','%s','%s','%s', %s);" \
                         % (self.pre_listen, listen_key, com_code, waybill_num, now_time, query_result, remark, user_no)
            self.db.execute(insert_sql)
            return True
        except Exception as e:
            print(e.args)

    def select_pre_listen(self, listen_key, user):
        select_sql = "SELECT com_code,waybill_num,remark,query_result FROM %s WHERE listen_key='%s' AND user='%s';"\
                     % (self.pre_listen, listen_key, user)
        result = self.db.execute(select_sql)
        if result <= 0:
            return None
        db_r = self.db.fetchone()
        return {"com_code": db_r[0], "waybill_num": db_r[1], "remark": db_r[2], "query_result": db_r[3]}

    def del_pre_listen(self, listen_key, user):
        select_sql = "DELETE FROM %s WHERE listen_key='%s' AND user='%s';" % (self.pre_listen, listen_key, user)
        result = self.db.execute(select_sql)
        if result <= 0:
            return False
        return True

    def select_com(self, com):
        try:
            if com != "":
                select_sql = "SELECT com_name,com_code FROM express_com WHERE com_name LIKE '%%%s%%' " \
                             "OR com_code LIKE '%%%s%%';" % (com, com)
            else:
                select_sql = "SELECT com_name,com_code FROM express_com;"
            self.db.execute(select_sql)
            com_info = []
            for item in self.db.fetchall():
                com_info.append({"com_name": item[0], "com_code": item[1]})
            return com_info
        except Exception as e:
            print(e.args)
            return []

    def send_wx(self, user_name, openid, status, com, waybill, remark, records):
        part_records = []
        len_info = len(records)
        for index in range(0, 3):
            if 3 - index > len_info:
                part_records.append({"time": "", "info": ""})
                continue
            part_records.append(records[len_info + index - 3])
        self.wx.send_express_template(user_name, openid, status, com, waybill, remark, part_records)

    def loop_query(self):
        eq = ExpressQuery()
        while True:
            # 睡眠5分钟
            print("Sleep 5 Minutes")
            sleep(300)
            # 最后最晚查询过的一条记录
            select_sql = "SELECT com_code,waybill_num,MIN(query_time),update_time,user,remark FROM listen_express;"
            self.db.execute(select_sql)
            record = self.db.fetchone()
            if record[0] is None:
                print("No Listen Record")
                continue
            com_code = record[0]
            waybill_num = record[1]
            update_time = record[3]
            user = record[4]
            remark = record[5]
            openid = self.uDB.select_openid(user)
            print("Start Handle %s %s" % (com_code, waybill_num))
            # 查询现在快速状态
            query_result = eq.query(com_code, waybill_num)
            if query_result["completed"] is True:
                print("%s %s completed" % (com_code, waybill_num))
                # 通知用户完成
                self.send_wx(user, openid, "completed", com_code, waybill_num, remark, query_result["express_info"])
                # 删除transport_express中对应的记录
                self.del_express_record(com_code, waybill_num)
                # 删除listen_express中对应的记录
                self.del_listen_record(com_code, waybill_num)
                # 将全部记录记入completed_express
                self.new_express_record(com_code, waybill_num, query_result["express_info"], True)
                continue
            express_info = query_result["express_info"]
            if len(express_info) <= 0:
                continue
            # 查询数据库中已有记录进行比对
            select_sql = "SELECT MAX(sign_time) FROM transport_express WHERE com_code='%s' AND waybill_num='%s';" % (com_code, waybill_num)
            result = self.db.execute(select_sql)
            max_sign_time = None
            if result > 0:
                max_sign_time = self.db.fetchone()[0]
            if max_sign_time is not None and max_sign_time >= datetime.strptime(express_info[-1]["time"], TIME_FORMAT):
                # 没有更新的快递信息
                # 判断是否超过5天没有更新记录
                if (datetime.now() - update_time).days >= 5:
                    print("Long time no info")
                    # 通知用户
                    self.send_wx(user, openid, "exception", com_code, waybill_num, remark, express_info)
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
                self.send_wx(user, openid, "transport", com_code, waybill_num, remark, express_info)
                # 添加运输记录
                add_record = []
                for record in express_info:
                    if max_sign_time is None or max_sign_time < datetime.strptime(record["time"], TIME_FORMAT):
                        add_record.append(record)
                self.new_express_record(com_code, waybill_num, add_record, False)
                # 更新update_time query_time
                self.update_listen_record(com_code, waybill_num, True, True)
