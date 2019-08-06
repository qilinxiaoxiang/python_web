#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 12:13
# @Author  : 项峥

conf = {
    "DATABASE": {
        "HOST": "",
        "PORT": 3306,
        "USER": "",
        "PASSWORD": "",
        "DATABASE": "",
    },

    "LOG_INFO": {
        "PATH": "",
        "LEVEL": "info",
        "MAX_BYTES": 10000000,  # 10MB
        "BACKUP_COUNT": 6,
    },

    "TASK_INTERVAL": {
        "GET_NEW_DATA": 8,  # unit second
        "COPY_IMPORTANT_DATA": 1,  # unit second
    },

    "SERVER": {
        "PORT": 5000,
    }
}
