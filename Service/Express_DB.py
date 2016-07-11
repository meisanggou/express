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
from Tools.MyEmail import MyEmailManager
from User_DB import UserDB

__author__ = 'zhouheng'

my_email = MyEmailManager()


class ExpressDB:

    def __init__(self):
        self.db = DB()
        self.db.connect()
        self.wx = WxManager()
        self.uDB = UserDB()
        self.completed_express = "completed_express"
        self.transport_express = "transport_express"
        self.history_express = "history_express"
        self.listen_express = "listen_express"
        self.pre_listen = "pre_listen"
        self.express_com = "express_com"

    def new_express_record(self, com_code, waybill_num, recodes, user_no, completed=False):
        if len(recodes) <= 0:
            return True
        insert_sql = "INSERT INTO %s (com_code,waybill_num,sign_time,sign_info,user_no,add_time) VALUES " \
                     % (self.completed_express if completed is True else self.transport_express)
        now_time = datetime.now().strftime(TIME_FORMAT)
        for recode in recodes:
            insert_sql += "('%s','%s','%s','%s',%s,'%s')," % (com_code, waybill_num, recode["time"], recode["info"], user_no, now_time)
        insert_sql = insert_sql[:-1] + ";"
        self.db.execute(insert_sql)
        return True

    def new_history_record(self, listen_no, com_code, waybill_num, remark, user_no):
        now_time = datetime.now().strftime(TIME_FORMAT)
        insert_sql = "INSERT INTO %s (listen_no,com_code, waybill_num,completed_time,remark,user_no) " \
                     "VALUES (%s,'%s','%s','%s','%s', %s);" \
                     % (self.history_express, listen_no, com_code, waybill_num, now_time, remark, user_no)
        self.db.execute(insert_sql)
        return True

    def del_express_record(self, com_code, waybill_num, user_no):
        del_sql = "DELETE FROM %s WHERE com_code='%s' AND waybill_num='%s' AND user_no=%s;" % (self.transport_express, com_code, waybill_num, user_no)
        self.db.execute(del_sql)
        return True

    def new_listen_record(self, com_code, waybill_num, remark, user_no):
        now_time = datetime.now().strftime(TIME_FORMAT)
        insert_sql = "INSERT INTO %s (com_code, waybill_num,update_time,query_time,remark,user_no) " \
                     "VALUES ('%s','%s','%s','%s','%s', %s);" \
                     % (self.listen_express, com_code, waybill_num, now_time, now_time, remark, user_no)
        self.db.execute(insert_sql)
        return True

    def update_listen_record(self, com_code, waybill_num, user_no, update=False, query=False):
        if update is False and query is False:
            return True
        update_sql = "UPDATE %s SET " % self.listen_express
        now_time = datetime.now().strftime(TIME_FORMAT)
        if update is True:
            update_sql += "update_time='%s'," % now_time
        if query is True:
            update_sql += "query_time='%s'," % now_time
        update_sql = update_sql[:-1] + " WHERE com_code='%s' AND waybill_num='%s' AND user_no=%s;" % (com_code, waybill_num, user_no)
        self.db.execute(update_sql)
        return True

    def del_listen_record(self, com_code, waybill_num, user_no):
        del_sql = "DELETE FROM %s WHERE com_code='%s' AND waybill_num='%s' AND user_no=%s;" % (self.listen_express, com_code, waybill_num, user_no)
        self.db.execute(del_sql)
        return True

    def select_listen_record(self, user_no, listen_no=None):
        select_sql = "SELECT listen_no,l.com_code,waybill_num,remark,com_name FROM %s AS l,%s AS c WHERE user_no=%s " \
                     "AND l.com_code=c.com_code" % (self.listen_express, self.express_com, user_no)
        if listen_no is not None:
            select_sql += " AND listen_no=%s" % listen_no
        select_sql += ";"
        result = self.db.execute(select_sql)
        listen_info = []
        for item in self.db.fetchall():
            listen_info.append({"listen_no": item[0], "com_code": item[1], "waybill_num": item[2], "remark": item[3],
                                "com_name": item[4]})
        return listen_info

    def check_listen_record(self, com_code, waybill_num, user_no):
        select_sql = "SELECT listen_no FROM %s WHERE com_code='%s' AND waybill_num='%s' AND user_no=%s;" % (self.listen_express, com_code, waybill_num, user_no)
        result = self.db.execute(select_sql)
        if result > 0:
            return True
        return False

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

    def select_pre_listen(self, listen_key, user_no):
        select_sql = "SELECT p.com_code,waybill_num,remark,query_result,com_name FROM %s AS p,%s AS c " \
                     "WHERE p.com_code=c.com_code AND listen_key='%s' AND user_no=%s;"\
                     % (self.pre_listen, self.express_com, listen_key, user_no)
        result = self.db.execute(select_sql)
        if result <= 0:
            return None
        db_r = self.db.fetchone()
        return {"com_code": db_r[0], "waybill_num": db_r[1], "remark": db_r[2], "query_result": db_r[3], "com_name": db_r[4]}

    def select_record_info(self, user_no, com_code, waybill_num):
        select_sql = "SELECT sign_time,sign_info,add_time FROM %s WHERE com_code='%s' AND waybill_num='%s' AND user_no=%s;" \
                     % (self.transport_express, com_code, waybill_num, user_no)
        self.db.execute(select_sql)
        records = []
        for item in self.db.fetchall():
            records.append({"time": item[0].strftime(TIME_FORMAT), "info": item[1],
                            "add_time": item[2].strftime(TIME_FORMAT)})
        return records

    def del_pre_listen(self, listen_key, user_no):
        select_sql = "DELETE FROM %s WHERE listen_key='%s' AND user_no='%s';" % (self.pre_listen, listen_key, user_no)
        result = self.db.execute(select_sql)
        if result <= 0:
            return False
        return True

    def select_com(self, com="", like=True):
        try:
            if com == "":
                select_sql = "SELECT com_name,com_code FROM express_com;"
            elif like is True:
                select_sql = "SELECT com_name,com_code FROM express_com WHERE com_name LIKE '%%%s%%' " \
                             "OR com_code LIKE '%%%s%%';" % (com, com)
            else:
                select_sql = "SELECT com_name,com_code FROM express_com WHERE com_code='%s';" % com
            self.db.execute(select_sql)
            com_info = []
            for item in self.db.fetchall():
                com_info.append({"com_name": item[0], "com_code": item[1]})
            return com_info
        except Exception as e:
            print(e.args)
            return []

    def send_wx(self, user_name, openid, status, com_code, waybill, remark, records):
        # 获得快递公司名称
        com_name = self.select_com(com_code, False)[0]["com_name"]
        part_records = []
        len_info = len(records)
        for index in range(0, 3):
            if 3 - index > len_info:
                part_records.append({"time": "", "info": ""})
                continue
            part_records.append(records[len_info + index - 3])
        self.wx.send_express_template(user_name, openid, status, com_name, com_code, waybill, remark, part_records)

    def loop_query(self):
        sleep_min = 5
        try:
            eq = ExpressQuery()
            while True:
                # 睡眠5分钟
                print("%s Sleep %s Minutes" % (datetime.now().strftime(TIME_FORMAT), sleep_min))
                sleep(sleep_min * 60)
                # 最后最晚查询过的一条记录
                select_sql = "SELECT com_code,waybill_num,query_time,update_time,user_no,remark,listen_no FROM listen_express WHERE query_time = (SELECT MIN(query_time) FROM listen_express);"
                result = self.db.execute(select_sql)
                if result <= 0:
                    print("%s No Listen Record." % datetime.now().strftime(TIME_FORMAT))
                    continue
                record = self.db.fetchone()
                if record[0] is None:
                    print("%s No Listen Record" % datetime.now().strftime(TIME_FORMAT))
                    continue
                com_code = record[0]
                waybill_num = record[1]
                update_time = record[3]
                user_no = record[4]
                remark = record[5]
                listen_no = record[6]
                user_info = self.uDB.select_user(user_no)
                openid = user_info["openid"]
                user_name = user_info["user_name"]
                print("%s Start Handle %s %s" % (datetime.now().strftime(TIME_FORMAT), com_code, waybill_num))
                # 查询现在快速状态
                query_result = eq.query(com_code, waybill_num)
                if query_result["completed"] is True:
                    print("%s %s %s completed" % (datetime.now().strftime(TIME_FORMAT), com_code, waybill_num))
                    # 通知用户完成
                    self.send_wx(user_name, openid, "completed", com_code, waybill_num, remark, query_result["express_info"])
                    # 删除transport_express中对应的记录
                    self.del_express_record(com_code, waybill_num, user_no)
                    # 删除listen_express中对应的记录
                    self.del_listen_record(com_code, waybill_num, user_no)
                    # 将全部记录记入completed_express
                    self.new_express_record(com_code, waybill_num, query_result["express_info"], user_no, True)
                    # 将监听记录插入history_express
                    self.new_history_record(listen_no, com_code, waybill_num, remark, user_no)
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
                        print("%s Long time no info" % datetime.now().strftime(TIME_FORMAT))
                        # 通知用户
                        self.send_wx(user_name, openid, "exception", com_code, waybill_num, remark, express_info)
                        # 删除transport_express中对应的记录
                        self.del_express_record(com_code, waybill_num, user_no)
                        # 删除listen_express中对应的记录
                        self.del_listen_record(com_code, waybill_num, user_no)
                    else:
                        # 更新 query_time
                        self.update_listen_record(com_code, waybill_num, user_no, False, True)
                else:
                    print("%s %s %s has new info." % (datetime.now().strftime(TIME_FORMAT), com_code, waybill_num))
                    # 通知用户
                    self.send_wx(user_name, openid, "transport", com_code, waybill_num, remark, express_info)
                    # 添加运输记录
                    add_record = []
                    for record in express_info:
                        if max_sign_time is None or max_sign_time < datetime.strptime(record["time"], TIME_FORMAT):
                            add_record.append(record)
                    self.new_express_record(com_code, waybill_num, add_record, user_no, False)
                    # 更新update_time query_time
                    self.update_listen_record(com_code, waybill_num, user_no, True, True)
        except Exception as e:
            error_message = "%s loop query exception :%s" % (datetime.now().strftime(TIME_FORMAT), str(e.args))
            print(error_message)
            my_email.send_system_exp("loop query function", "", error_message, 0)
            print("%s run again" % datetime.now().strftime(TIME_FORMAT))
            self.loop_query()
