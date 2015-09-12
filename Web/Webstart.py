#! /usr/bin/env python
# coding: utf-8

import thread
from Tools.Wx import WxManager
from flask import Flask
from Web.views import express_wx_view as express_wx_view_blueprint


__author__ = 'zhouheng'

wx = WxManager()
thread.start_new_thread(wx.write_token(), ())

msg_web = Flask("__name__")
msg_web.register_blueprint(express_wx_view_blueprint)

if __name__ == '__main__':
    msg_web.run(host="0.0.0.0", threaded=True, debug=True, port=1100)
