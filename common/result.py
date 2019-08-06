#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 12:33
# @Author  : 项峥


def success_result(data=None):
    return {
        "info": "success",
        "code": 0,
        "data": data,
    }


def error_result(info, code=-1, data=None):
    return {
        "info": info,
        "code": code,
        "data": data,
    }
