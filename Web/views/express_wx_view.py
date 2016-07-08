#!/user/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Blueprint, request, jsonify
from Tools.MyEmail import MyEmailManager
from Tools.Wx import WxManager

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
        # request_data = request.data
        # args = ""
        # for key in dict(request.args).keys():
        #     args += "%s=%s&" % (key, request.args[key])
        # args += "request_ip=%s" % request.headers["X-Real-Ip"]
        # res_result = requests.post(APIV1_service + '/api/v1/express/wx/?' + args, data=request_data)
        # if res_result.status_code / 100 != 2:
        #     return ""
        # return res_result.text
        request_ip = request.headers["X-Real-Ip"]
        # 判断请求IP是否是微信服务器IP
        if wx.check_wx_ip(request_ip) is False:
            return jsonify({"status": 800, "message": "check wx service fail"})
        signature = request.args["signature"]
        timestamp = request.args["timestamp"]
        nonce = request.args["nonce"]
        request_data = request.data
        return wx.handle_msg(request_data, signature, timestamp, nonce)
    except Exception as e:
        my_email.send_system_exp(request.url, request.data, str(e), 0)
        return ""
