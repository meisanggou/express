# encoding: utf-8
# !/usr/bin/python

from time import time
from flask import Flask, request, g, jsonify
from Tools.Mysql_db import DB

__author__ = 'zhouheng'

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def add_cross_domain_headers(resp):
    resp.headers["Access-Control-Allow-Methods"] = "POST,GET,PUT,DELETE"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Authorization"


def before_request_func():
    g.run_begin = time()
    if request.method == "OPTIONS" and "geneacdms" in request.args and request.args["geneacdms"] == "test":
        return jsonify({"status": 2000002, "message": "test success"})


def after_request_func(resp):
    add_cross_domain_headers(resp)
    return resp


def handle_500_func(e):
    level = "error"
    info = request.data[:400] + "\n" + str(e)
    info = info[:500].replace("\\", "\\\\").replace("\'", "\\'")
    full_path = request.full_path[:200]
    run_end = time()
    if "run_begin" not in g:
        run_begin = run_end
    else:
        run_begin = g.run_begin
    run_time = run_end - run_begin
    insert_sql = "INSERT INTO run_log(run_begin,host,url,method,account,ip,level,info,run_time) " \
                 "VALUES (%s,'%s','%s','%s','%s',%s,'%s','%s',%s);" \
                 % (run_begin, request.host_url, full_path, request.method, "", g.request_IP, level, info, run_time)
    try:
        db = DB()
        db.execute(insert_sql)
        db.close()
    except Exception as e:
        print(e)
    resp = jsonify({"status": 2009901, "message": "Internal Error"})
    add_cross_domain_headers(resp)
    return resp


def create_app():
    app = Flask('__name__')

    app.before_request_funcs.setdefault(None, []).append(before_request_func)
    app.after_request_funcs.setdefault(None, []).append(after_request_func)

    app.error_handler_spec[None][500] = handle_500_func

    @app.route("/ping/", methods=["GET"])
    def ping():
        return jsonify({"status": 2000002, "message": "ping success"})

    return app
