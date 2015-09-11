# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Express_DB import ExpressDB
from flask import Flask, request

msg_service = Flask('__name__')

if __name__ == '__main__':
    eDB = ExpressDB()
    result = eDB.check_completed_express()
    if result is False:
        eDB.create_completed_express(True)
    result = eDB.check_listen_express()
    if result is False:
        eDB.create_listen_express(True)
    result = eDB.check_transport_express()
    if result is False:
        eDB.create_transport_express(True)
    msg_service.run(host="0.0.0.0", port=2157)
