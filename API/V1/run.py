#! /usr/bin/env python
# coding: utf-8


__author__ = 'zhouheng'

import sys
sys.path.append('..')

from API.V1 import msg_api
from Tools.Mysql_db import DB

db = DB()
db.connect()
db.execute("SHOW TABLES")
print(db.fetchall())

if __name__ == '__main__':
    msg_api.run(host="0.0.0.0", port=1523)
