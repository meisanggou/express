# encoding: utf-8
# !/usr/bin/python

import json
import datetime
from flask import request
from API.V1 import db, msg_api
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
        msg_signature = None
        if "encrypt_type" in request.args:
            if request.args["encrypt_type"] == "aes":
                msg_signature = request.args["msg_signature"]
        request_data = request.data
        return wx.handle_msg(request_data, signature, timestamp, nonce, msg_signature)
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


@msg_api.route('/api/v1/express/wx/openid/', methods=["POST"])
def account_code():
    """
    :param  account passwd openid
    :return: If success, return
    """
    try:
        run_begin = datetime.datetime.now()
        # 判断参数是否齐全
        try:
            request_data = json.loads(request.data)
        except ValueError as ve:
            print(ve.args)
            return json.dumps({"status": 403, "message": "Need Json String Data"})
        # 判断用户登录的用户名和密码是否正确
        try:
            account = request_data["account"]
            wx_id = request_data["openid"]
            auth = requests.post(auth_url + "/userconfirm/",
                                 data=json.dumps({"account": account, "passwd": request_data["passwd"]}))
        except KeyError as ke:
            print(ke.args)
            error_message = str(ke.args)
            return json.dumps({"status": 403, "message": "Bad Request %s" % error_message})
        if auth.status_code != 200:
            return json.dumps({"status": 108, "message": "Auth error, unable to access user confirm service."})
        res = json.loads(auth.text)
        if res["status"] != 2:
            return json.dumps({"status": 102, "message": "User confirm failed : %s" % res["message"]})
        # service 方法关联wx_id和account
        res = requests.put(user_url + "/user/wx_id/",
                           data=json.dumps({"account": account, "wx_id": wx_id}))
        r = res.json()
        if r["status"] == 001:
            wx.send_bind_template_thread(account, wx_id)
            run_time = (datetime.datetime.now() - run_begin).total_seconds()
            r["run_time"] = run_time
            return json.dumps(r)
        return res.text
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return json.dumps({"status": 701, "message": error_message})


@msg_api.route('/api/v1/express/wx/openid/', methods=["GET"])
def openid_code():
    """
    :param  account passwd [check]
    :return: If success, return
    """
    try:
        run_begin = datetime.datetime.now()
        # 判断参数是否齐全
        try:
            request_data = json.loads(request.data)
        except ValueError as ve:
            print(ve.args)
            return json.dumps({"status": 403, "message": "Need Json String Data"})
        try:
            code = request_data["code"]
        except KeyError as ke:
            print(ke.args)
            error_message = str(ke.args)
            return json.dumps({"status": 403, "message": "Bad Request %s" % error_message})
        # 调用wx 方法通过code获得openid
        openid = wx.get_openid(code)
        if openid == "":
            return json.dumps({"status": 801, "message": "Get OpenID Fail"})
        if "check" in request_data and request_data["check"] is True:
            select_url = "SELECT account FROM user_config WHERE wx_id='%s'" % openid
            result = db.execute(select_url)
            if result > 0:
                account = db.fetchone()[0]
                run_time = (datetime.datetime.now() - run_begin).total_seconds()
                return json.dumps({"status": 001, "message": "check success", "run_time": run_time, "data": account})
            else:
                return json.dumps({"status": 802, "message": "NOT FIND RECORD", "data": openid})
        else:
            run_time = (datetime.datetime.now() - run_begin).total_seconds()
            return json.dumps({"status": 001, "message": "get openid success", "data": openid, "run_time": run_time})
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return json.dumps({"status": 701, "message": error_message})


@msg_api.route('/api/v1/express/wx/check/', methods=["GET"])
def get_account_code():
    try:
        run_begin = datetime.datetime.now()
        # 判断参数是否齐全
        try:
            request_data = json.loads(request.data)
        except ValueError as ve:
            print(ve.args)
            return json.dumps({"status": 403, "message": "Need Json String Data"})
        try:
            wx_id = request_data["openid"]
        except KeyError as ke:
            print(ke.args)
            error_message = str(ke.args)
            return json.dumps({"status": 403, "message": "Bad Request %s" % error_message})
        # 调用wx 方法执行更新自定义菜单
        select_url = "SELECT account FROM user_config WHERE wx_id='%s'" % wx_id
        result = db.execute(select_url)
        if result > 0:
            account = db.fetchone()[0]
            run_time = (datetime.datetime.now() - run_begin).total_seconds()
            return json.dumps({"status": 001, "message": "get success", "run_time": run_time, "data": account})
        else:
            return json.dumps({"status": 400, "message": "NOT FIND RECORD"})
    except Exception, e:
        print(e.args)
        error_message = str(e.args)
        my_email.send_system_exp(request.url, request.data, error_message, 0)
        return json.dumps({"status": 701, "message": error_message})

