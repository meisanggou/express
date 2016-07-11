# encoding: utf-8
# !/usr/bin/python
import sys
sys.path.append('..')
from Tools.Mysql_db import DB

__author__ = 'zhouheng'


class UserDB:

    def __init__(self):
        self.db = DB()
        self.db.connect()
        self.user = "express_user"

    def new_express_user(self, user_name, openid):
        if len(openid) != 28:
            return False
        insert_sql = "INSERT INTO %s (user_name,openid) VALUES ('%s','%s');" % (self.user, user_name, openid)
        self.db.execute(insert_sql)
        return True

    def update_express_user(self, user_name, openid):
        if len(openid) != 28:
            return False
        update_sql = "UPDATE %s SET user_name='%s' WHERE openid='%s';" % (self.user, user_name, openid)
        self.db.execute(update_sql)
        return True

    def select_user(self, user_no=None, openid=None, user_name=None):
        select_sql = "SELECT user_no,user_name,openid FROM %s WHERE " % self.user
        if user_no is not None:
            select_sql += "user_no=%s;" % user_no
        elif openid is not None:
            select_sql += "openid='%s';" % openid
        elif user_name is not None:
            select_sql += "user_name='%s';" % user_name
        else:
            return None
        result = self.db.execute(select_sql)
        if result <= 0:
            return None
        db_r = self.db.fetchone()
        return {"user_no": db_r[0], "user_name": db_r[1], "openid": db_r[2]}
