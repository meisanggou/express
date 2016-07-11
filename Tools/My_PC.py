#! /usr/bin/env python
# coding: utf-8
__author__ = 'ZhouHeng'


import os
from re import search
from platform import system
from socket import gethostname
from getpass import getuser


class My_PCManager:

    def __init__(self):
        self.current_os = system().lower()

    def get_ip(self):
        try:
            command = ""
            if self.current_os == "linux":
                command = "ifconfig"
            elif self.current_os == "windows":
                command = "ipconfig"
            else:
                return ["0.0.0.0"]
            result = os.popen(command)
            lines = result.readlines()
            result.close()
            ip_list = []
            for line in lines:
                search_result = search("\d+\.\d+\.\d+\.\d+", line)
                if search_result is not None:
                    ip_list.append(search_result.group())
            return ip_list
        except Exception as e:
            error_messge = "get ip exception : %s" % str(e.args)
            print(error_messge)
            return [error_messge]

    def get_user(self):
        try:
            return getuser()
        except Exception as e:
            error_message = "get user exception : %s" % str(e.args)
            print(error_message)
            return error_message

    def get_hostname(self):
        try:
            return gethostname()
        except Exception as e:
            error_message = "get hostname exception : %s" % str(e.args)
            print(error_message)
            return error_message

    def get_info(self):
        ip = "IP: %s " % "  ".join(self.get_ip())
        hostname = "HostName: %s " % self.get_hostname()
        current_user = "Current User: %s" % self.get_user()
        info = "%s %s %s" % (ip, hostname, current_user)
        return info
if __name__ == "__main__":
    pc = My_PCManager()
    pc_info = pc.get_info()