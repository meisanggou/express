#!/user/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import sys
from flask import Blueprint, request
from Tools.MyEmail import MyEmailManager
from Tools.Wx import WxManager
from Web import APIV1_service

sys.path.append('..')

__author__ = 'Zhouheng'

my_email = MyEmailManager()
wx = WxManager()


express_wx_view = Blueprint('express_wx_view', __name__)

my_email = MyEmailManager()
wx = WxManager()


@express_wx_view.route("/express/wx/ping/", methods=["GET"])
def ping():
    return "true"


# 微信主动调用方法
@express_wx_view.route("/express/wx/", methods=["GET"])
def check_signature():
    try:
        signature = request.args["signature"]
        timestamp = request.args["timestamp"]
        nonce = request.args["nonce"]
        echostr = request.args["echostr"]
        if wx.check_signature(signature, timestamp, nonce):
            return echostr
        return "false"
    except Exception as e:
        error_message = "check sign exp: %s url:" % str(e.args)
        # my_email.send_system_exp(request.url, "wx", error_message, 0)
        return "false"


# 微信主动调用方法
@express_wx_view.route("/express/wx/", methods=["POST"])
def get_wx_msg():
    try:
        # http://meisanggou.club/wx/?signature=b836cf610e29f42fdb35341b30f429f9e75cbd7a&timestamp=1437184393&nonce=1535827132&encrypt_type=aes&msg_signature=70ee22b541b20b9561e2474fd1ee01a6f17a9d38
        request_data = request.data
        args = ""
        for key in dict(request.args).keys():
            args += "%s=%s&" % (key, request.args[key])
        args += "request_ip=%s" % request.headers["X-Real-Ip"]
        res_result = requests.post(APIV1_service + '/api/v1/express/wx/?' + args, data=request_data)
        if res_result.status_code / 100 != 2:
            return ""
        return res_result.text
    except Exception as e:
        print(e.args)
        my_email.send_system_exp(request.url, request.data, str(e.args), 0)
        return ""


@express_wx_view.route("/express/wx/token/", methods=["GET"])
def wx_token():
    try:
        res_result = requests.get(APIV1_service + '/api/v1/express/wx/token/')
        if res_result.status_code / 100 != 2:
            return json.dumps({"status": 701, "message": "Internal error %s" % str(res_result.status_code)})
        return res_result.text
    except Exception, e:
        error_message = str(e.args)
        print(e.args)
        return json.dumps({"status": 701, "message": "Internal error %s" % error_message})


@express_wx_view.route("/express/wx/menu/", methods=["GET"])
def create_menu():
    try:
        res_result = requests.put(APIV1_service + '/api/v1/express/wx/menu/')
        if res_result.status_code / 100 != 2:
            return json.dumps({"status": 701, "message": "Internal error %s" % str(res_result.status_code)})
        return res_result.text
    except Exception, e:
        error_message = str(e.args)
        print(e.args)
        return json.dumps({"status": 701, "message": "Internal error %s" % error_message})



