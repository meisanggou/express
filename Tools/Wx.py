#! /usr/bin/env python
# coding: utf-8

import sys
import datetime
import requests
import json
import time
from time import sleep
import tempfile
from hashlib import sha1
import binascii
import re
from lxml import etree
from MyEmail import MyEmailManager
from Tools import query_service_url

__author__ = 'ZhouHeng'

my_email = MyEmailManager()


class WxManager:
    def __init__(self):
        self.token_file = ""
        self.get_token_file()
        self.appID = "wx38e949d41b9d1053"
        self.appsecret = "c2eaf806849fa05cb12e202c55c2aae2"
        self.access_token = ""
        self.wx_ip = []
        self.expires_time = datetime.datetime.now()
        self.token = "meisanggou"

        self.text_str_temp = """<xml><ToUserName><![CDATA[%(to_user)s]]></ToUserName><FromUserName>
        <![CDATA[%(from_user)s]]></FromUserName><CreateTime><![CDATA[%(create_time)s]]></CreateTime>
        <MsgType>text</MsgType><Content><![CDATA[%(content)s]]></Content></xml>"""
        self.bind_remind = u"您的微信账号还没绑定用户名。请回复绑定+空格+用户名进行绑定，用户名可以是数字，" \
                           u"汉字或者字母，用户名长度不可低于1个字符不可超过15个字。例如绑定 meisanggou"
        self.bind_repeat = u"您的微信账号已经绑定%s，无需重复绑定"
        self.bind_used = u"您想绑定的用户名%s已经被绑定，请更换用户名重试"
        self.waybill_error = u"您想监听的运单 %s 不能监听"
        self.explain_success = u"***恭喜您***\n 您提供的%s公司运单号为%s备注为%s的快递可以监听,监听密钥：%s。" \
                               u"请直接复制本条消息回复，即可开始监听。"
        self.invalid_listen_key = u"无效的监听密钥"
        self.start_listen = u"已经开始监听您的快递%s %s"
        self.listen_info = u"欢迎您使用我们的应用监听快递信息\n首先你先点击监听快递，再点击快递公司查看我们" \
                           u"支持的快递公司\n如果我们已经支持您要监听的快递公司，" \
                           u"回复快递+空格+快递公司名称+空格+运单号+空格+运单备注（例如：快递 申通快递 229255098587 电池）即可监听"

    # 基础
    def get_token_file(self):
        self.token_file = tempfile.gettempdir() + "/express_wx.token"

    def write_token(self):
        try:
            while True:
                access_token = self.get_wx_token()
                if access_token == "":
                    sleep(60)
                    continue
                write = open(self.token_file, "w")
                write.write(access_token)
                write.close()
                sleep(5400)  # sleep 90 minutes
        except Exception as e:
            error_message = str(e.args)
            print(error_message)

    def get_wx_token(self, freq=0):
        if freq >= 5:
            my_email.send_system_exp("get wx access token ", freq, "didn't make it, many times", 0)
            return ""
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" \
              % (self.appID, self.appsecret)
        res = requests.get(url)
        if res.status_code == 200:
            r = json.loads(res.text)
            if "access_token" in r:
                self.access_token = r["access_token"]
                self.expires_time = datetime.datetime.now() + datetime.timedelta(seconds=r["expires_in"])
                return self.access_token
            else:
                my_email.send_system_exp("get wx access token", url, res.text, 0)
        elif res.status_code / 100 == 5:
            my_email.send_system_exp("get wx access token get again:%s" % freq, url, str(res.status_code), 0)
            return self.get_access_token(freq + 1)
        else:
            my_email.send_system_exp("get wx access token", url, str(res.status_code), 0)
            return ""

    def get_access_token(self):
        try:
            read = open(self.token_file)
            return read.read()
            read.close()
        except Exception as e:
            error_message = str(e.args)
            my_email.send_system_exp("read wx access token ", self.token_file, error_message, 0)
            return ""

    def get_sha_value(self, timestamp, nonce, encrypt=None):
        temp_arr = [self.token, timestamp, nonce]
        if encrypt is not None:
            temp_arr.append(encrypt)
        temp_arr.sort()
        temp_str = "".join(temp_arr)
        temp_sha1 = binascii.b2a_hex(sha1(temp_str).digest())
        return temp_sha1

    def check_signature(self, signature, timestamp, nonce):
        temp_sha1 = self.get_sha_value(timestamp, nonce)
        if temp_sha1 == signature:
            return True
        else:
            return False

    def check_wx_ip(self, ip, freq=0):
        if freq >= 5:
            return False
        if ip in self.wx_ip:
            return True
        url = "https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token=%s" % self.get_access_token()
        res = requests.get(url)
        if res.status_code == 200:
            r = json.loads(res.text)
            if "ip_list" in r:
                self.wx_ip = r["ip_list"]
                if ip in self.wx_ip:
                    return True
                else:
                    my_email.send_system_exp("get wx ip false", url, ip + " | " + res.text, 0)
                    return False
            else:
                my_email.send_system_exp("get wx ip", url, res.text, 0)
                return False
        elif res.status_code / 100 == 5:
            my_email.send_system_exp("get wx ip get again:%s" % freq, url, str(res.status_code), 0)
            return self.check_wx_ip(ip, freq + 1)
        else:
            my_email.send_system_exp("get wx ip fail", url, str(res.status_code), 0)
            return False

    # 自定义菜单管理
    def create_menu(self, menu_json_str=""):
        try:
            url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % self.get_access_token()
            if menu_json_str == "":
                read_json = open("../Tools/wx_menu.json")
                btn_str = read_json.read()
                btn_str = btn_str.decode("gbk").encode("utf8")
            else:
                btn_str = menu_json_str
            res = requests.post(url, data=btn_str)
            r = json.loads(res.text)
            if r["errcode"] != 0:
                my_email.send_system_exp("create wx menu", url, res.text, 0)
                return res.text
            return res.text
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("create wx menu exp", url, str(e.args), 0)
            return str(e.args)

    # 接收消息
    def handle_msg(self, msg, signature, timestamp, nonce):
        try:
            # 判断消息是否加密 检验消息是否合法
            check_result = self.check_signature(signature, timestamp, nonce)
            if check_result is False:
                return ""
            xml_msg = etree.fromstring(msg)
            msg_type = xml_msg.find("MsgType").text
            if msg_type == "text":
                return_str = self.handle_msg_text(xml_msg)
            elif msg_type == "event":
                return_str = self.handle_msg_event(xml_msg)
            elif msg_type == "voice":
                return_str = self.handle_msg_voice(xml_msg)
            else:
                return_str = self.handle_msg_other(xml_msg)
            return return_str
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg exp", msg, str(e.args), 0)
            return ""

    def handle_msg_text(self, xml_msg):
        try:
            content = xml_msg.find("Content").text
            from_user = xml_msg.find("FromUserName").text
            if len(content) > 2 and content[0:3] == u"快递 ":
                content = self.handle_msg_text_express(content, from_user)
            elif len(content) > 2 and content[0:3] == u"绑定 ":
                content = self.handle_msg_text_express_user(content, from_user)
            elif len(content) > 2 and content[0:3] == "***":
                content = self.handle_msg_text_add_listen(content, from_user)
            elif len(content) > 2 and content[:3] == u"考研 ":
                content = self.handle_msg_ky(content)
            elif len(content) > 4 and content[0:5] == u"我的快递 ":
                content = self.handle_msg_text_look_listen(content, from_user)
            to_user = xml_msg.find("ToUserName").text
            create_time = str(int(time.time()))
            res = {"to_user": from_user, "from_user": to_user, "create_time": create_time, "content": content}
            return self.text_str_temp % res
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg text exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    def handle_msg_text_express(self, content, openid):
        no_prefix = content[2:].strip(" ")
        response = requests.post(query_service_url + "/explain/", data=json.dumps({"content": no_prefix, "openid": openid}))
        if response.status_code / 100 == 2:
            result = response.json()
            if result["status"] == 001:
                return self.explain_success % (result["data"]["com_name"], result["data"]["waybill_num"], result["data"]["remark"], result["data"]["listen_key"])
            elif result["status"] == 410:
                return self.bind_remind
            elif result["status"] == 421:
                return self.waybill_error % result["message"]
        return content

    def handle_msg_text_express_user(self, content, openid):
        no_prefix = content[3:]
        response = requests.post(query_service_url + "/bind/", data=json.dumps({"user_name": no_prefix, "openid": openid}))
        if response.status_code / 100 == 2:
            if response.json()["status"] == 001:
                data = response.json()["data"]
                if data["old"] is None:
                    return u"您已成功将用户名%s绑定到您的微信账号" % data["new"]
                else:
                    return u"您已成功将原来用户名%s更改为%s" % (data["old"], data["new"])
            elif response.json()["status"] == 412:
                return self.bind_repeat % no_prefix
            elif response.json()["status"] == 411:
                return self.bind_used % no_prefix
            else:
                return response.text
        else:
            return response.status_code
        return content

    def handle_msg_text_add_listen(self, content, openid):
        regex = self.explain_success[10:] % (u'[a-zA-Z\u4e00-\u9fa5]+?', "[0-9]{10,30}", "[\s\S]*?", "([a-z0-9]{32})")
        keys = re.findall(regex, content)
        if len(keys) != 1:
            return content
        response = requests.post(query_service_url + "/add/", data=json.dumps({"listen_key": keys[0], "openid": openid}))
        if response.status_code / 100 == 2:
            if response.json()["status"] == 001:
                listen_key = response.json()["data"]
                return self.start_listen % (listen_key["com_name"], listen_key["waybill_num"])
            elif response.json()["status"] == 410:
                return self.bind_remind
            elif response.json()["status"] == 422:
                return self.invalid_listen_key
            else:
                return response.text
        else:
            return response.status_code
        return content

    def handle_msg_text_look_listen(self, content, openid):
        listen_no = re.findall("[\d]+", content)
        if len(listen_no) != 1:
            return content
        if len(listen_no[0]) > 10:
            return content
        response = requests.get(query_service_url + "/look/", data=json.dumps({"listen_no": int(listen_no[0]), "openid": openid}))
        if response.status_code / 100 == 2:
            if response.json()["status"] == 001:
                return u"即将推送给您"
            elif response.json()["status"] == 410:
                return self.bind_remind
            else:
                return response.text
        else:
            return response.status_code
        return content

    def handle_msg_ky(self, content):
        try:
            info = content[3:].strip(" ")
            request_url_format = "http://www.kfszsb.com/ajax_2014.asp?act=yjs&ksbh=%s&bmh=&zjhm=%s&t=0.34829033026471734"
            if info == u"马铭章" or info == u"傻梦" or info == u"乖乖":
                request_url = request_url_format % ('102856210201028', '411481199308247826')
            else:
                sp_info = info.split(" ")
                ky_info = []
                for item in sp_info:
                    if item != " ":
                        ky_info.append(item)
                if len(ky_info) < 2:
                    return u"输入信息有误"
                request_url = request_url_format % (ky_info[0], ky_info[1])
            res = requests.get(request_url)
            if res.status_code != 200:
                return content
            return u"请求地址%s\n返回信息%s" % (request_url, res.text)
        except Exception as e:
            error_message = str(e.args)
            return error_message

    def handle_msg_voice(self, xml_msg):
        try:
            from_user = xml_msg.find("FromUserName").text
            to_user = xml_msg.find("ToUserName").text
            r = xml_msg.find("Recognition")

            content = u"被你戳到痛点了，还不能识别你发的东西！" if r is None else r.text if r.text != "" else u"未能识别您的语音消息，请用普通话再说一次"
            create_time = str(int(time.time()))
            res = {"to_user": from_user, "from_user": to_user, "create_time": create_time, "content": content}
            return self.text_str_temp % res
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg voice exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    def handle_msg_event(self, xml_msg):
        try:
            event = xml_msg.find("Event").text
            if event == "scancode_waitmsg":
                return self.handle_msg_event_scan(xml_msg)
            if event.lower() == "click":
                return self.handle_msg_event_click(xml_msg)
            else:
                return self.handle_msg_other(xml_msg)
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg event exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    def handle_msg_event_scan(self, xml_msg):
        try:
            scan_info = xml_msg.find("ScanCodeInfo")
            scan_result = scan_info.find("ScanResult").text
            from_user = xml_msg.find("FromUserName").text
            to_user = xml_msg.find("ToUserName").text

            content = u"扫描结果为:" + scan_result
            create_time = str(int(time.time()))
            res = {"to_user": from_user, "from_user": to_user, "create_time": create_time, "content": content}
            return self.text_str_temp % res
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg event scan exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    def handle_msg_event_click(self, xml_msg):
        try:
            key = xml_msg.find("EventKey").text
            from_user = xml_msg.find("FromUserName").text
            to_user = xml_msg.find("ToUserName").text
            content = key
            if key == "express_com":
                response = requests.get(query_service_url + "/com/")
                if response.status_code / 100 == 2:
                    if response.json()["status"] == 001:
                        com_info = response.json()["data"]
                        content = u"我们暂时支持的快递公司有：\n"
                        for ci in com_info:
                            content += ci["com_name"] + " "
                    elif response.json()["status"] == 410:
                        content = self.bind_remind
                    else:
                        content = response.text
                else:
                    content = response.status_code
            elif key == "listen_express":
                content = self.listen_info
            elif key == "my_express":
                response = requests.get(query_service_url + "/mine/", data=json.dumps({"openid": from_user}))
                if response.status_code / 100 == 2:
                    if response.json()["status"] == 001:
                        listen_info = response.json()["data"]
                        content = u"您监听的快递有：\n"
                        for li in listen_info:
                            content += "编号：%s 快递公司：%s 运单号：%s 运单备注：%s\n" % (li["listen_no"], li["com_name"],
                                                                           li["waybill_num"], li["remark"])
                        content += "回复我的快递+编号(例如：我的快递 1)查看快递运送信息"
                    elif response.json()["status"] == 410:
                        content = self.bind_remind
                    else:
                        content = response.text
                else:
                    content = response.status_code
            create_time = str(int(time.time()))
            res = {"to_user": from_user, "from_user": to_user, "create_time": create_time, "content": content}
            return self.text_str_temp % res
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg event scan exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    def handle_msg_other(self, xml_msg):
        try:
            from_user = xml_msg.find("FromUserName").text
            to_user = xml_msg.find("ToUserName").text

            content = u"被你戳到痛点了，还不能识别你发的东西！"
            create_time = str(int(time.time()))
            res = {"to_user": from_user, "from_user": to_user, "create_time": create_time, "content": content}
            return self.text_str_temp % res
        except Exception as e:
            print(e.args)
            my_email.send_system_exp("handle msg text exp", etree.tostring(xml_msg), str(e.args), 0)
            return ""

    # 发送消息
    def send_express_template(self, user_name, openid, status, com, com_code, waybill, remark, records):
        try:
            if status not in ("transport", "completed", "exception", "mine"):
                return "fail"
            temp_status = {"transport": "6atTNaoeH-Xaqf4Q-tBYInLs_fqR0h1dcNOfAgIfUBc",
                           "completed": "OFeSZXk6wNQVmX1GJ8P67bXe6FOoEMcMo1s49jIE-Nc",
                           "exception": "SHun5Ndh8NQDOCkFoi8XM5Lur5TyD1_9LrndC3QN9G0",
                           "mine": "Plj7_3JKJHB0EbAs7XdkLzTQ4l5Mo-IuxsXbN3TpXRc"}
            url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.get_access_token()
            request_data = {}
            request_data["template_id"] = temp_status[status]
            request_data["touser"] = openid
            request_data["url"] = "http://m.kuaidi100.com/index_all.html?type=%s&postid=%s" % (com_code, waybill)
            request_data["data"] = {}
            request_data["data"]["user_name"] = {"value": user_name, "color": "#173177"}
            request_data["data"]["com"] = {"value": com, "color": "#000000"}
            request_data["data"]["waybill"] = {"value": waybill, "color": "#173177"}
            request_data["data"]["remark"] = {"value": remark, "color": "#173177"}
            request_data["data"]["time1"] = {"value": records[2]["time"], "color": "#000000"}
            request_data["data"]["info1"] = {"value": records[2]["info"], "color": "#173177"}
            request_data["data"]["time2"] = {"value": records[1]["time"], "color": "#000000"}
            request_data["data"]["info2"] = {"value": records[1]["info"], "color": "#000000"}
            request_data["data"]["time3"] = {"value": records[0]["time"], "color": "#173177"}
            request_data["data"]["info3"] = {"value": records[0]["info"], "color": "#000000"}
            res = requests.post(url, data=json.dumps(request_data))
            if res.status_code == 200:
                print(res.text)
            else:
                print(res.status_code)
            return "success"
        except Exception as e:
            print(e.args)

    # 网页服务
    def get_openid(self, code, freq=0):
        if freq >= 5:
            return ""
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&" \
              "grant_type=authorization_code" % (self.appID, self.appsecret, code)
        res = requests.get(url)
        if res.status_code == 200:
            r = json.loads(res.text)
            if "openid" in r:
                return r["openid"]
            else:
                my_email.send_system_exp("get wx openid by code fail", url, res.text, 0)
                return ""
        elif res.status_code / 100 == 5:
            my_email.send_system_exp("get wx openid by code get again:%s" % freq, url, str(res.status_code), 0)
            return self.get_openid(freq + 1)
        else:
            my_email.send_system_exp("get wx openid by code exp", url, str(res.status_code), 0)
            return ""
