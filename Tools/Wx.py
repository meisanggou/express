#! /usr/bin/env python
# coding: utf-8

import datetime
import requests
import json
import time
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
        self.explain_success = u"***恭喜您***\n%s。" \
                               u"请直接复制本条消息回复，即可开始监听。"
        self.explain_no_records = u"***有点问题***\n%s，暂时无法查询到任何快递记录。" \
                               u"请检查快递信息，或者直接复制本条消息回复强制进行监听。"
        self.invalid_listen_key = u"无效的监听密钥"
        self.start_listen = u"已经开始监听您的快递%s %s"
        self.listen_info = u"欢迎您使用我们的应用监听快递信息\n首先你先点击监听快递，再点击快递公司查看我们" \
                           u"支持的快递公司\n如果我们已经支持您要监听的快递公司，" \
                           u"回复快递+空格+快递公司名称+空格+运单号+空格+运单备注（例如：快递 申通快递 229255098587 电池）即可监听"
        self.token_error_code = [41001, 40001, 42001, 40014, 42007]

    @staticmethod
    def _request(method, url, **kwargs):
        kwargs["verify"] = False
        return requests.request(method, url, **kwargs)

    # 基础
    def get_wx_token(self, freq=0):
        if freq >= 5:
            return ""
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" \
              % (self.appID, self.appsecret)
        res = self._request("GET", url)
        if res.status_code == 200:
            r = res.json()
            if "access_token" in r:
                self.access_token = r["access_token"]
                self.expires_time = datetime.datetime.now() + datetime.timedelta(seconds=r["expires_in"])
                return self.access_token
        elif res.status_code / 100 == 5:
            return self.get_wx_token(freq + 1)
        else:
            return ""

    def refresh_token(self):
        self.get_wx_token()

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
        url = "https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token=%s" % self.access_token
        res = requests.get(url)
        if res.status_code == 200:
            r = res.json()
            if "ip_list" in r:
                self.wx_ip = r["ip_list"]
                if ip in self.wx_ip:
                    return True
                else:
                    # self.my_email.send_system_exp("check wx ip fail", url, ip + " | " + res.text, 0)
                    return False
            if "errcode" in r:
                error_code = r["errcode"]
                if error_code in self.token_error_code:
                    if freq < 2:
                        self.get_wx_token()
                        return self.check_wx_ip(ip=ip, freq=freq+1)
            else:
                my_email.send_system_exp("get wx ip", url, res.text, 0)
                return False
        elif res.status_code / 100 == 5:
            my_email.send_system_exp("get wx ip get again:%s" % freq, url, str(res.status_code), 0)
            return self.check_wx_ip(ip, freq + 1)
        else:
            my_email.send_system_exp("get wx ip fail", url, str(res.status_code), 0)
            return False

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
        response = requests.post(query_service_url + "/explain/", json={"content": no_prefix, "openid": openid})
        if response.status_code / 100 == 2:
            result = response.json()
            if result["status"] == 001:
                info = u"您提供的%s公司运单号为%s备注为%s的快递可以监听,监听密钥：%s" % (result["data"]["com_name"], result["data"]["waybill_num"], result["data"]["remark"], result["data"]["listen_key"])
                return self.explain_success % info
            elif result["status"] == 003:
                info = u"您提供的%s公司运单号为%s备注为%s的快递可以监听,监听密钥：%s" % (result["data"]["com_name"], result["data"]["waybill_num"], result["data"]["remark"], result["data"]["listen_key"])
                return self.explain_no_records % info
            elif result["status"] == 410:
                return self.bind_remind
            elif result["status"] == 421:
                return self.waybill_error % result["message"]
        return content

    def handle_msg_text_express_user(self, content, openid):
        no_prefix = content[3:]
        response = requests.post(query_service_url + "/bind/", json={"user_name": no_prefix, "openid": openid})
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
        regex = u"您提供的%s公司运单号为%s备注为%s的快递可以监听,监听密钥：%s" % (u'[a-zA-Z\u4e00-\u9fa5]+?', "[0-9]{10,30}", "[\s\S]*?", "([a-z0-9]{32})")
        keys = re.findall(regex, content)
        if len(keys) != 1:
            return content
        response = requests.post(query_service_url + "/add/", json={"listen_key": keys[0], "openid": openid})
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
        response = requests.get(query_service_url + "/look/", json={"listen_no": int(listen_no[0]), "openid": openid})
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
                response = requests.get(query_service_url + "/mine/", json={"openid": from_user})
                if response.status_code / 100 == 2:
                    if response.json()["status"] == 001:
                        listen_info = response.json()["data"]
                        content = u"您监听的快递有：\n"
                        for li in listen_info:
                            content += u"编号：%s 快递公司：%s 运单号：%s 运单备注：%s\n" % (li["listen_no"], li["com_name"],
                                                                           li["waybill_num"], li["remark"])
                        content += u"回复我的快递+编号(例如：我的快递 1)查看快递运送信息"
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
    def _request_tencent(self, url, method, freq=0, **kwargs):
        access_token = kwargs.pop("access_token", self.access_token)
        request_url = url % {"access_token": access_token}
        res = self._request(method, request_url, **kwargs)
        if res.status_code != 200:
            if freq > 2:
                return False, res.status_code
            return self._request_tencent(url, method, freq+1, **kwargs)
        r = res.json()
        if "errcode" in r:
            error_code = r["errcode"]
            if error_code == 0:
                return True, r
            if error_code in self.token_error_code:
                self.refresh_token()
                if freq > 2:
                    return False, r
                return self._request_tencent(url, method, freq+1, **kwargs)
            else:
                return False, r
        return True, r

    def _send_template(self, template_id, touser, url, key_value):
        request_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%(access_token)s"
        message_data = {}
        for key in key_value:
            message_data[key] = key_value[key]
        request_data = {"template_id": template_id, "touser": touser, "url": url, "data": message_data}
        return self._request_tencent(request_url, "POST", json=request_data)

    def send_express_template(self, user_name, openid, status, com, com_code, waybill, remark, records):
        if status not in ("transport", "completed", "exception", "mine"):
            return "fail"
        temp_status = {"transport": "6atTNaoeH-Xaqf4Q-tBYInLs_fqR0h1dcNOfAgIfUBc",
                       "completed": "OFeSZXk6wNQVmX1GJ8P67bXe6FOoEMcMo1s49jIE-Nc",
                       "exception": "SHun5Ndh8NQDOCkFoi8XM5Lur5TyD1_9LrndC3QN9G0",
                       "mine": "Plj7_3JKJHB0EbAs7XdkLzTQ4l5Mo-IuxsXbN3TpXRc"}
        url = "http://m.kuaidi100.com/index_all.html?type=%s&postid=%s&callbackurl=" % (com_code, waybill)

        key_value = {}
        key_value["user_name"] = {"value": user_name, "color": "#173177"}
        key_value["com"] = {"value": com, "color": "#000000"}
        key_value["waybill"] = {"value": waybill, "color": "#173177"}
        key_value["remark"] = {"value": remark, "color": "#173177"}
        key_value["time1"] = {"value": records[2]["time"], "color": "#000000"}
        key_value["info1"] = {"value": records[2]["info"], "color": "#173177"}
        key_value["time2"] = {"value": records[1]["time"], "color": "#000000"}
        key_value["info2"] = {"value": records[1]["info"], "color": "#000000"}
        key_value["time3"] = {"value": records[0]["time"], "color": "#173177"}
        key_value["info3"] = {"value": records[0]["info"], "color": "#000000"}

        return self._send_template(temp_status[status], openid, url, key_value)
