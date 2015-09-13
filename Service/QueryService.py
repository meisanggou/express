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
        user = uDB.select_user(request_data["openid"])
        return json.dumps({"status": 001, "message": "query success", "data": user})
    else:
        return json.dumps({"status": 400})
    old_user = uDB.select_user(openid)
    if old_user is None:
        if uDB.select_openid(user) is not None:
            return json.dumps({"status": 411})
        uDB.new_express_user(user, openid)
    else:
        if old_user == user:
            return json.dumps({"status": 412})
        if uDB.select_openid(user) is not None:
            return json.dumps({"status": 411})
        uDB.update_express_user(user, openid)
    return json.dumps({"status": 001, "message": "bind success", "data": {"old": old_user, "new": user}})


@msg_service.route('/explain/', methods=["POST"])
def explain_express():
    request_data = json.loads(request.data)
    content = request_data["content"]
    openid = request_data["openid"]
    user = uDB.select_user(openid)
    if user is None:
        return json.dumps({"status": 410})
    infos = re.split('[,，]', content)
    if len(infos) < 2:
        return json.dumps({"status": 400})
    com_code = infos[0]
    waybill_num = infos[1]
    check_result, message, query_result = eb.check_waybill(com_code, waybill_num)
    if check_result is False:
        return json.dumps({"status": 421, "message": message})
    eDB.new_pre_listen(message, com_code, waybill_num, "", user, json.dumps(query_result))
    data = {"com_code": com_code, "waybill_num": waybill_num, "listen_key": message}
    return json.dumps({"status": 001, "message": "check success", "data": data})


@msg_service.route('/add/', methods=["POST"])
def add_listen():
    request_data = json.loads(request.data)
    openid = request_data["openid"]
    listen_key = request_data["listen_key"]
    user = uDB.select_user(openid)
    if user is None:
        return json.dumps({"status": 410})
    listen_info = eDB.select_pre_listen(listen_key, user)
    if listen_info is None:
        return json.dumps({"status": 422})
    # 添加到运输记录中
    recodes = json.loads(listen_info["query_result"])
    eDB.new_express_record(listen_info["com_code"], listen_info["waybill_num"], recodes)
    # 添加到监听列表中
    eDB.new_listen_record(listen_info["com_code"], listen_info["waybill_num"], listen_info["remark"], user)
    return json.dumps({"status": 001, "message": "listen success", "data": listen_info})

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
    result = eDB.check_pre_listen()
    if result is False:
        eDB.create_pre_listen(True)
    result = uDB.check_express_user()
    if result is False:
        uDB.create_express_user(True)
    # kd100_info = eq.kd100("yuantong", "200246227212")
    # eDB.new_express_record("yuantong", "200246227212", kd100_info["express_info"], False)
    # eDB.new_listen_record("sto", "229255098587", "zhou5315938@163.com")
    thread.start_new_thread(eDB.loop_query, ())
    msg_service.run(host="0.0.0.0", port=1191)
