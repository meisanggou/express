# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Express_DB import ExpressDB
from Express_Query import ExpressQuery
from Express_Basic import ExpressBasic
from User_DB import UserDB
from flask import Flask, request
import thread
import json
import re

msg_service = Flask('__name__')


@msg_service.route('/ping/', methods=["GET"])
def ping():
    return "true"


@msg_service.route('/bind/', methods=["POST"])
def bind():
    request_data = json.loads(request.data)
    if "user" in request_data and "openid" in request_data:
        user = request_data["user"]
        openid = request_data["openid"]
        search_result = re.search('[^0-9a-zA-Z\u4e00-\u9fa5]', user)
        if search_result is not None:
            return json.dumps({"status": 400})
        if len(user) <= 0 or len(user) > 15:
            return json.dumps({"status": 400})
    elif "openid" in request_data:
        user = uDB.select_express_user(request_data["openid"])
        return json.dumps({"status": 001, "message": "query success", "data": user})
    else:
        return json.dumps({"status": 400})
    old_user = uDB.select_express_user(openid)
    if old_user is None:
        uDB.new_express_user(user, openid)
    else:
        if old_user == user:
            return json.dumps({"status": 412})
        uDB.update_express_user(user, openid)
    return json.dumps({"status": 001, "message": "bind success", "data": {"old": old_user, "new": user}})


@msg_service.route('/explain/', methods=["POST"])
def explain_express():
    request_data = json.loads(request.data)
    content = request_data["content"]
    openid = request_data["openid"]
    if uDB.select_express_user(openid) is None:
        return json.dumps({"status": 410})
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
    uDB = UserDB()
    result = eDB.check_completed_express()
    if result is False:
        eDB.create_completed_express(True)
    result = eDB.check_listen_express()
    if result is False:
        eDB.create_listen_express(True)
    result = eDB.check_transport_express()
    if result is False:
        eDB.create_transport_express(True)
    result = uDB.check_express_user()
    if result is False:
        uDB.create_express_user(True)
    # kd100_info = eq.kd100("yuantong", "200246227212")
    # eDB.new_express_record("yuantong", "200246227212", kd100_info["express_info"], False)
    # eDB.new_listen_record("sto", "229255098587", "zhou5315938@163.com")
    thread.start_new_thread(eDB.loop_query, ())
    msg_service.run(host="0.0.0.0", port=1191)
