#! /usr/bin/env python
# coding: utf-8


import sys
sys.path.append('..')
from API_V1 import msg_api

__author__ = 'zhouheng'

if __name__ == '__main__':
    msg_api.run(host="0.0.0.0", port=1201)
