# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Express_DB import ExpressDB
from Service.Express_Query import ExpressQuery
from flask import Flask, request
import thread
import json

msg_service = Flask('__name__')


@msg_service.route('/add/', methods=["POST"])
def add_listen():
    request_data = json.loads(request.data)
    com_code = request_data["com_code"]
    waybill_num = request_data["waybill"]
    call_email = request_data["email"]
    new_result = eDB.new_listen_record(com_code, waybill_num, call_email)
    if new_result is True:
        return json.dumps({"status": 000, "message": "Add Success"})
    else:
        return json.dumps({"status": 500, "message": "Internal error"})

if __name__ == '__main__':
    eDB = ExpressDB()
    eq = ExpressQuery()
    result = eDB.check_completed_express()
    if result is False:
        eDB.create_completed_express(True)
    result = eDB.check_listen_express()
    if result is False:
        eDB.create_listen_express(True)
    result = eDB.check_transport_express()
    if result is False:
        eDB.create_transport_express(True)
    # kd100_info = eq.kd100("yuantong", "200246227212")
    # eDB.new_express_record("yuantong", "200246227212", kd100_info["express_info"], False)
    # eDB.new_listen_record("sto", "229255098587", "zhou5315938@163.com")
    thread.start_new_thread(eDB.loop_query(), ())
    msg_service.run(host="0.0.0.0", port=2157)
