# encoding: utf-8
# !/usr/bin/python

__author__ = 'zhouheng'

from Express_DB import ExpressDB
from Express_Query import ExpressQuery
from Express_Basic import ExpressBasic
from User_DB import UserDB
from flask import request
import thread
import json
import re
from Service import create_app

msg_service = create_app()


@msg_service.route('/bind/', methods=["POST"])
def bind():
    request_data = json.loads(request.data)
    if "user_name" in request_data and "openid" in request_data:
        user_name = request_data["user_name"].strip(" ")
        openid = request_data["openid"]
        search_result = re.search(u'[^\w\u4e00-\u9fa5]', user_name)
        if search_result is not None:
            return json.dumps({"status": 400})
        if len(user_name) <= 0 or len(user_name) > 15:
            return json.dumps({"status": 400})
    elif "openid" in request_data:
        user = uDB.select_user(request_data["openid"])
        return json.dumps({"status": 001, "message": "query success", "data": user})
    else:
        return json.dumps({"status": 400})
    old_user = uDB.select_user(openid=openid)
    if old_user is None:
        print("enter")
        if uDB.select_user(user_name=user_name) is not None:
            return json.dumps({"status": 411})
        uDB.new_express_user(user_name, openid)
    else:
        if old_user["user_name"] == user_name:
            return json.dumps({"status": 412})
        if uDB.select_user(user_name=user_name) is not None:
            return json.dumps({"status": 411})
        uDB.update_express_user(user_name, openid)
    return json.dumps({"status": 001, "message": "bind success", "data": {"old": old_user["user_name"], "new": user_name}})


@msg_service.route('/explain/', methods=["POST"])
def explain_express():
    try:
        request_data = json.loads(request.data)
        content = request_data["content"]
        openid = request_data["openid"]
        user = uDB.select_user(openid=openid)
        if user is None:
            return json.dumps({"status": 410})
        user_no = user["user_no"]
        infos = content.split(" ")
        infos_len = len(infos)
        for index in range(1, infos_len):
            if infos[infos_len - index] == "":
                infos.remove(infos[infos_len - index])
        if len(infos) < 2:
            return json.dumps({"status": 400})
        com = infos[0]
        if len(com) <= 0:
            return json.dumps({"status": 421, "message": u"快递公司不明确"})
        # 查询快递是否存在
        com_info = eDB.select_com(com)
        if len(com_info) == 0:
            return json.dumps({"status": 421, "message": u"快递公司不支持"})
        if len(com_info) > 1:
            return json.dumps({"status": 421, "message": u"快递公司不明确"})
        com_code = com_info[0]["com_code"]
        com_name = com_info[0]["com_name"]
        waybill_num = infos[1]
        check_result, message, query_result = eb.check_waybill(com_code, waybill_num)
        if check_result is False:
            return json.dumps({"status": 421, "message": message})
        check_result = eDB.check_listen_record(com_code, waybill_num, user_no)
        if check_result is True:
            return json.dumps({"status": 421, "message": u"已经在监听"})
        remark = ""
        if len(infos) >= 3:
            remark = infos[2][:10]
        eDB.new_pre_listen(message, com_code, waybill_num, remark, user_no, json.dumps(query_result))
        data = {"com_code": com_code, "waybill_num": waybill_num, "listen_key": message, "com_name": com_name, "remark": remark}
        return json.dumps({"status": 001, "message": "check success", "data": data})
    except Exception as e:
        return json.dumps({"status": 500, "message": str(e.args)})


@msg_service.route('/add/', methods=["POST"])
def add_listen():
    request_data = json.loads(request.data)
    openid = request_data["openid"]
    listen_key = request_data["listen_key"]
    user = uDB.select_user(openid=openid)
    if user is None:
        return json.dumps({"status": 410})
    user_no = user["user_no"]
    listen_info = eDB.select_pre_listen(listen_key, user_no)
    if listen_info is None:
        return json.dumps({"status": 422})
    # 添加到运输记录中
    recodes = json.loads(listen_info["query_result"])
    eDB.new_express_record(listen_info["com_code"], listen_info["waybill_num"], recodes, user_no)
    # 添加到监听列表中
    eDB.new_listen_record(listen_info["com_code"], listen_info["waybill_num"], listen_info["remark"], user_no)
    eDB.del_pre_listen(listen_key, user_no)
    return json.dumps({"status": 001, "message": "listen success", "data": listen_info})


@msg_service.route('/look/', methods=["GET"])
def look_listen():
    request_data = json.loads(request.data)
    openid = request_data["openid"]
    listen_no = request_data["listen_no"]
    user = uDB.select_user(openid=openid)
    if user is None:
        return json.dumps({"status": 410})
    user_no = user["user_no"]
    listen_info = eDB.select_listen_record(user_no, listen_no)
    if len(listen_info) <= 0:
        return json.dumps({"status": 423, "message": u"查找的快递编号不存在"})
    listen_info = listen_info[0]
    express_record = eDB.select_record_info(user_no, listen_info["com_code"], listen_info["waybill_num"])
    eDB.send_wx(user["user_name"], user["openid"], "mine", listen_info["com_code"], listen_info["waybill_num"],
                listen_info["remark"], express_record)
    return json.dumps({"status": 001, "message": "listen success", "data": {"express_info": listen_info,
                                                                            "express_record": express_record,
                                                                            "user_info": user}})


@msg_service.route('/com/', methods=["GET"])
def get_com():
    com_info = eDB.select_com("")
    return json.dumps({"status": 001, "message": "get success", "data": com_info})


@msg_service.route('/mine/', methods=["GET"])
def mine_express():
    request_data = json.loads(request.data)
    openid = request_data["openid"]
    user = uDB.select_user(openid=openid)
    if user is None:
        return json.dumps({"status": 410})
    user_no = user["user_no"]
    listen_info = eDB.select_listen_record(user_no)
    return json.dumps({"status": 001, "message": "get success", "data": listen_info})


if __name__ == '__main__':
    eDB = ExpressDB()
    eq = ExpressQuery()
    eb = ExpressBasic()
    uDB = UserDB()
    thread.start_new_thread(eDB.loop_query, ())
    msg_service.run(host="0.0.0.0", port=1191)
