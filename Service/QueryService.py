# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Express_DB import ExpressDB
from Express_Query import ExpressQuery
from Express_Basic import ExpressBasic
from flask import Flask, request
import thread
import json
import re

msg_service = Flask('__name__')


@msg_service.route('/ping/', methods=["GET"])
def ping():
    return "true"


@msg_service.route('/explain/', methods=["POST"])
def explain_express():
    request_data = json.loads(request.data)
    content = request_data["content"]
    infos = re.split('[,，]', content)
    if len(infos) < 2:
        return json.dumps({"status": 400})
    if eb.check_waybill(infos[0], infos[1]) is False:
        return json.dumps({"status": 400})
    data = u"您监听%s的快递，运单号：%s" % (infos[0], infos[1])
    return json.dumps({"status": 001, "message": "check success", "data": data})


@msg_service.route('/add/', methods=["POST"])
def add_listen():
    request_data = json.loads(request.data)
    com_code = request_data["com_code"]
    waybill_num = request_data["waybill"]
    user = request_data["user"]
    remark = request_data["remark"]
    new_result = eDB.new_listen_record(com_code, waybill_num, remark, user)
    if new_result is True:
        return json.dumps({"status": 000, "message": "Add Success"})
    else:
        return json.dumps({"status": 500, "message": "Internal error"})

if __name__ == '__main__':
    eDB = ExpressDB()
    eq = ExpressQuery()
    eb = ExpressBasic()
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
    thread.start_new_thread(eDB.loop_query, ())
    msg_service.run(host="0.0.0.0", port=1191)
