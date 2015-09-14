# encoding: utf-8
# !/usr/bin/env python

import MySQLdb
import logging
import time
import threading
import ConfigParser
import sys
import os

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
current_filename = sys.argv[0][sys.argv[0].rfind(os.sep) + 1:sys.argv[0].rfind(os.extsep)]
logging.basicConfig(filename=current_filename + '_DB.log', filemode='w')

remote_host = "gene.ac"
local_host = "127.0.0.1"


class DB(object):
    conn = None
    cursor = None
    _sock_file = ''

    def __init__(self, local=False):
        try:
            if local is True:
                self.host = local_host
            else:
                self.host = remote_host
            config = ConfigParser.ConfigParser()
            config.read('/etc/my.cnf')
            self._sock_file = ""  # config.get('mysqld', 'socket')
        except ConfigParser.NoSectionError:
            self._sock_file = ''

    def connect(self):
        logging.info(time.ctime() + " : connect to mysql server..")
        if self._sock_file != '':
            self.conn = MySQLdb.connect(host=self.host, port=3306, user='msg',
                                        passwd='msg1237', db='express', charset='utf8',
                                        unix_socket=self._sock_file)
            self.cursor = self.conn.cursor()
        else:
            self.conn = MySQLdb.connect(host=self.host, port=3306, user='msg',
                                        passwd='msg1237', db='express', charset='utf8')
            self.cursor = self.conn.cursor()

        self.conn.autocommit(True)

    # 线程函数
    def thread(self):
        t = threading.Thread(target=self.conn.ping, args=())
        t.setDaemon(True)
        t.start()
        t.join(4)
        if t.isAlive():
            return 0
        else:
            return 1

    def execute(self, sql_query):
        try:
            logging.info(time.ctime() + " : " + sql_query)
            # 重启超过五次则不再重启
            i = 0
            while i < 3 and self.thread() != 1:
                self.close()
                self.connect()
                self.cursor = self.conn.cursor()
                i += 1
            if i == 3:
                return logging.error(time.ctime() + "execute failed")
            handled_item = self.cursor.execute(sql_query)
        except Exception, e:
            logging.error(e.args)
            logging.info("Reconnecting..")
            self.connect()
            self.cursor = self.conn.cursor()
            logging.info(time.ctime() + " : " + sql_query)
            handled_item = self.cursor.execute(sql_query)
        return handled_item

    def fetchone(self):
        try:
            logging.info(time.ctime() + " : fetchone")
            one_item = self.cursor.fetchone()
        except Exception, e:
            logging.error(e.args)
            logging.info(time.ctime() + " : fetchone failed, return ()")
            one_item = ()
        return one_item

    def fetchall(self):
        try:
            logging.info(time.ctime() + " : fetchall")
            all_item = self.cursor.fetchall()
        except Exception, e:
            logging.error(e.args)
            logging.info(time.ctime() + " : fetchall failed, return ()")
            all_item = ()
        return all_item

    def close(self):
        logging.info(time.ctime() + " : close connect")
        if self.cursor:
            self.cursor.close()
        self.conn.close()

    def format_string(self, str):
        return MySQLdb.escape_string(str)

    def create_table(self, table_name, table_desc, force=False):
        try:
            show_sql = "SHOW TABLES LIKE '%s';" % table_name
            result = self.execute(show_sql)
            execute_message = ""
            if result == 1:
                if force:
                    del_sql = "DROP TABLE  %s;" % table_name
                    self.execute(del_sql)
                    execute_message += "Delete The Original Table %s \n" % table_name
                else:
                    return "%s Table Already Exists" % table_name
            create_table_sql = "CREATE TABLE %s (" % table_name
            for value in table_desc:
                create_table_sql += "%s %s" % (value[0], value[1])
                if value[2] == "NO":
                    create_table_sql += " NOT NULL"
                if value[3] == "PRI":
                    create_table_sql += " PRIMARY KEY"
                if value[4] is not None:
                    create_table_sql += " default %s" % value[4]
                if value[5] != "":
                    create_table_sql += " %s" % value[5]
                create_table_sql += ","
            create_table_sql = create_table_sql[:-1] + ") DEFAULT CHARSET=utf8;"
            self.execute(create_table_sql)
            execute_message += "Create Table %s Success \n" % table_name
            return execute_message
        except Exception, e:
            error_message = str(e.args)
            print(error_message)
            return "fail:%s." % error_message

    def check_table(self, table_name, table_desc):
        try:
            check_sql = "DESC %s;" % table_name
            self.execute(check_sql)
            # desc = self.fetchall()
            # if len(desc) != len(table_desc):
            #     return False
            # for i in range(0, len(desc)-1):
            #     desc_item = desc[i]
            #     table_desc_item = table_desc[i]
            #     if len(desc_item) != len(table_desc_item):
            #         return False
            #     for j in range(0, len(desc_item)-1):
            #         if desc_item[j] != table_desc_item[j]:
            #             return False
            return True
        except Exception, e:
            error_message = str(e.args)
            print(error_message)
            return False
