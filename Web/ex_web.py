#! /usr/bin/env python
# coding: utf-8
import sys
sys.path.append("..")
from Tools.Wx import WxManager
from flask import Flask
from Web.views import express_wx_view as express_wx_view_blueprint


__author__ = 'zhouheng'

wx = WxManager()
msg_web = Flask("__name__")
msg_web.register_blueprint(express_wx_view_blueprint)

if __name__ == '__main__':
    msg_web.run(host="0.0.0.0", port=1100)
