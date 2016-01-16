# encoding: utf-8
# !/usr/bin/python

import json
import datetime
from flask import request
from API_V1 import db, msg_api
from Tools.Wx import WxManager
from Tools.MyEmail import MyEmailManager

wx = WxManager()
my_email = MyEmailManager()

__author__ = 'zhouheng'


@msg_api.route('/api/v1/express/ping/', methods=["GET"])
def ping():
    return "true"


# 以下为微信相关消息处理
@msg_api.route('/api/v1/express/wx/', methods=["POST"])
def handle_wx_msg():
    """
    :param  need xml data
    :return: If success, return xml data
    """
    try:
        request_ip = request.args["request_ip"]
        # 判断请求IP是否是微信服务器IP
        if wx.check_wx_ip(request_ip) is False:
            return json.dumps({"status": 800, "message": "check wx service fail"})
        signature = request.args["signature"]
        timestamp = request.args["timestamp"]
        nonce = request.args["nonce"]
        request_data = request.data
        return wx.handle_msg(request_data, signature, timestamp, nonce)
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return ""


@msg_api.route('/api/v1/express/wx/token/', methods=["GET"])
def get_wx_token():
    """
    :param  account (system account) passwd
    :return: If success, return token value like
            dZSHBqaluUFypTZIZUl_lJ166StsuLGg0fXxQaPIKJlp2T0LIQt98c60Bo2iHBpPQEmvIAQFPe4I98Wr5ET0jZNYIb4IUqOwDFzIDD64mAE
    """
    try:
        run_begin = datetime.datetime.now()
        # 调用wx 方法执行获得token
        token = wx.get_access_token()
        run_time = (datetime.datetime.now() - run_begin).total_seconds()
        return json.dumps({"status": 001, "message": "Get Success", "data": token, "run_time": run_time})
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return json.dumps({"status": 701, "message": error_message})


@msg_api.route('/api/v1/express/wx/menu/', methods=["PUT"])
def update_wx_menu():
    """
    :param  account (system account) passwd
    :return: If success, return {
                                    "status": 1,
                                    "message": "{\"errcode\":0,\"errmsg\":\"ok\"}",
                                    "run_time": 2.095
                                }
    """
    try:
        run_begin = datetime.datetime.now()

        # 调用wx 方法执行更新自定义菜单
        run_message = wx.create_menu()
        run_time = (datetime.datetime.now() - run_begin).total_seconds()
        return json.dumps({"status": 001, "message": run_message, "run_time": run_time})
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return json.dumps({"status": 701, "message": error_message})
