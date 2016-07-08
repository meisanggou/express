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

