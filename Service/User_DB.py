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
        self.user_desc = [
            ["user_name", "int(11)", "NO", "PRI", None, "auto_increment"],
            ["user_name", "varchar(15)", "NO", "", None, ""],
            ["openid", "char(28)", "NO", "", None, ""]
        ]

    def create_express_user(self, force=False):
        return self.db.create_table(self.user, self.user_desc, force)

    def check_express_user(self):
        return self.db.check_table(self.user, self.user_desc)

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

    def select_user(self, openid):
        select_sql = "SELECT user_name FROM %s WHERE openid='%s';" % (self.user, openid)
        result = self.db.execute(select_sql)
        if result <= 0:
            return None
        return self.db.fetchone()[0]

    def select_openid(self, user):
        select_sql = "SELECT openid FROM %s WHERE user_name='%s';" % (self.user, user)
        result = self.db.execute(select_sql)
        if result <= 0:
            return None
        return self.db.fetchone()[0]
