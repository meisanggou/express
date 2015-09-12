# encoding: utf-8
# !/usr/bin/python
import sys

sys.path.append('..')

__author__ = 'zhouheng'


from flask import Flask
from Tools.Mysql_db import DB

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

msg_api = Flask(__name__)

db = DB()
db.connect()

import api_express
