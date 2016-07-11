#! /usr/bin/env python
# coding: utf-8

import MySQLdb
import json
import os

__author__ = 'ZhouHeng'


class TableToolManager:

    def __init__(self, mysql_host):
        # "rdsikqm8sr3rugdu1muh3.mysql.rds.aliyuncs.com"
        self.conn = MySQLdb.connect(host=mysql_host, port=3306, user='msg', passwd='msg1237', db='express', charset='utf8')
        self.cursor = self.conn.cursor()

    def list_table(self):
        sql = "SELECT TABLE_NAME, CREATE_TIME,TABLE_COMMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA='clinic' AND TABLE_TYPE='BASE TABLE';"
        self.cursor.execute(sql)
        table_list = []
        for item in self.cursor.fetchall():
            table_list.append({"table_name": item[0], "create_time": item[1], "table_comment": item[2]})
        return True, table_list

    def get_table_info(self, table_name):
        sql = "SELECT COLUMN_NAME, COLUMN_TYPE,COLUMN_KEY,COLUMN_DEFAULT,EXTRA,COLUMN_COMMENT,IS_NULLABLE " \
              "FROM information_schema.columns WHERE TABLE_NAME='%s' AND TABLE_SCHEMA='clinic';" % table_name
        self.cursor.execute(sql)
        column_info = []
        for item in self.cursor.fetchall():
            column_info.append({"column_name": item[0], "column_type": item[1], "column_key": item[2],
                                "column_default": item[3], "extra": item[4], "column_comment": item[5],
                                "is_nullable": item[6]})
        return True, column_info

    def write_to_file(self, file_path):
        result, t_list = self.list_table()
        mul_table_info = []
        if result is False:
            return False, t_list
        for t in t_list:
            table_info = {"table_name": t["table_name"], "table_comment": t["table_comment"], "table_cols": []}
            result, cols_info = self.get_table_info(table_info["table_name"])
            if result is False:
                return False, cols_info
            for col in cols_info:
                col_info = {"col_name": col["column_name"], "col_type": col["column_type"], "col_comment": col["column_comment"]}
                if col["extra"] == "auto_increment":
                    col_info["auto_increment"] = True
                    col_info["pri_key"] = True
                elif col["column_key"] == "PRI":
                    col_info["pri_key"] = True
                elif col["column_key"] == "UNI":
                    col_info["uni_key"] = True
                if col["column_default"] is not None:
                    col_info["default_value"] = col["column_default"]
                if col["is_nullable"] == "YES":
                    col_info["allow_null"] = True
                table_info["table_cols"].append(col_info)
            mul_table_info.append(table_info)
        write_json = open(file_path, "w")
        write_json.write(json.dumps(mul_table_info, indent=2))
        write_json.close()
        return True, "success"


class DBTool:

    def __init__(self, mysql_host):
        # "rdsikqm8sr3rugdu1muh3.mysql.rds.aliyuncs.com"
        self.conn = MySQLdb.connect(host=mysql_host, port=3306, user='msg', passwd='msg1237', db='express', charset='utf8')
        self.cursor = self.conn.cursor()

    def check_table(self, table_name):
        try:
            check_sql = "DESC %s;" % table_name
            self.cursor.execute(check_sql)
            return True
        except Exception, e:
            error_message = str(e.args)
            print(error_message)
            return False

    def create_table(self, table_desc):
        if type(table_desc) != dict:
            return False, "table_desc need dict"
        if "table_name" not in table_desc or "table_cols" not in table_desc:
            return False, "Bad table_desc, nedd table_name and table_cols"
        table_name = table_desc["table_name"]
        table_cols = table_desc["table_cols"]
        if self.check_table(table_name) is True:
            return False, "Table exist."
        create_table_sql = "CREATE TABLE %s (" % table_name
        primary_key = []
        uni_key = []
        for col in table_cols:
            if "col_name" not in col or "col_type" not in col:
                return False, "Bad col, need col_name and col_type"
            col_name = col["col_name"]
            create_table_sql += "%s %s" % (col_name, col["col_type"])
            if "allow_null" in col and col["allow_null"] is True:
                pass
            else:
                create_table_sql += " NOT NULL"
            if "auto_increment" in col and col["auto_increment"] is True:
                create_table_sql += " auto_increment"
                primary_key.append(col_name)
            elif "pri_key" in col and col["pri_key"] is True:
                primary_key.append(col_name)
            if "uni_key" in col and col["uni_key"] is True:
                uni_key.append(col_name)
            if "default_value" in col and col["default_value"] is not None:
                if col["default_value"] == "":
                    create_table_sql += " default ''"
                else:
                    create_table_sql += " default %s" % col["default_value"]

            if "col_comment" in col and col["col_comment"] is not None:
                create_table_sql += " COMMENT '%s'" % col["col_comment"]
            create_table_sql += ","
        if len(primary_key) > 0:
            create_table_sql += " PRIMARY KEY (%s)," % ",".join(primary_key)
        if len(uni_key) > 0:
            for key in uni_key:
                create_table_sql += " UNIQUE KEY ({0}),".format(key)
        if "table_comment" in table_desc and table_desc["table_comment"] != "":
            create_table_sql = create_table_sql[:-1] + ") COMMENT '%s' DEFAULT CHARSET=utf8;" % table_desc["table_comment"]
        else:
            create_table_sql = create_table_sql[:-1] + ") DEFAULT CHARSET=utf8;"
        self.cursor.execute(create_table_sql)
        execute_message = "CREATE TABLE %s Success \n" % table_name
        return True, execute_message

    def create_mul_table(self, mul_table_desc):
        if type(mul_table_desc) != list:
            return False, "mul_table_desc need list"
        mul_len = len(mul_table_desc)
        if mul_len <= 0:
            return False, "mul_table_desc len is 0"
        fail_index = []
        for i in range(mul_len):
            table_desc = mul_table_desc[i]
            result, message = self.create_table(table_desc)
            if result is False:
                fail_index.append((i, message))
        return True, fail_index

    def create_from_json_file(self, json_file):
        if os.path.isfile(json_file) is False:
            print("json file not exist")
            return False, "json file not exist"
        read_json = open(json_file)
        json_content = read_json.read()
        read_json.close()
        try:
            json_desc = json.loads(json_content, "utf-8")
        except ValueError as ve:
            print(ve)
            return False, "File content not json"
        result, message = self.create_mul_table(json_desc)
        return result, message

    def create_from_dir(self, desc_dir):
        if os.path.isdir(desc_dir) is False:
            print("desc dir not exist")
            return False, "desc dir not exist"
        desc_files = os.listdir(desc_dir)
        create_info = []
        for item in desc_files:
            if not item.endswith(".json"):
                continue
            file_path = desc_dir+ "/" + item
            result, info = self.create_from_json_file(file_path)
            create_info.append({"file_path": file_path, "create_result": result, "create_info": info})
        return True, create_info

# # example
# dbt = DBTool("192.168.120.2")
# result = dbt.create_from_dir("../Basic_Service")
# print(result)

