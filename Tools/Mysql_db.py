# encoding: utf-8
# !/usr/bin/env python

import MySQLdb

__author__ = 'zhouheng'

"""
Usage:
    from Mysql_db import DB
     db = DB()
     db.execute(sql)
     db.fetchone()
     db.fetchall()
     :return same as MySQLdb
"""

remote_host = "gene.ac"


class DB(object):
    conn = None
    cursor = None
    _sock_file = ''

    def __init__(self):
        self.host = remote_host

    def connect(self):
        self.conn = MySQLdb.connect(host=self.host, port=3306, user='msg', passwd='msg1237', db='express', charset='utf8')
        self.cursor = self.conn.cursor()
        self.conn.autocommit(True)

    def execute(self, sql_query, args=None, freq=0):
        if self.cursor is None:
            self.connect()
        try:
            handled_item = self.cursor.execute(sql_query, args=args)
        except MySQLdb.Error as error:
            print(error)
            if freq >= 5:
                raise Exception(error)
            self.connect()
            return self.execute(sql_query=sql_query, args=args, freq=freq+1)
        return handled_item

    def execute_insert(self, table_name, args):
        keys = dict(args).keys()
        sql_query = "INSERT INTO %s (%s) VALUES (%%(%s)s);" % (table_name, ",".join(keys), ")s,%(".join(keys))
        return self.execute(sql_query, args=args)

    def fetchone(self):
        one_item = self.cursor.fetchone()
        return one_item

    def fetchall(self):
        all_item = self.cursor.fetchall()
        return all_item

    def close(self):
        if self.cursor:
            self.cursor.close()
        self.conn.close()

    def format_string(self, str):
        return MySQLdb.escape_string(str)
