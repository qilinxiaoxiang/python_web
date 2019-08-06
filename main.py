#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 16:08
# @Author  : 项峥
import time

from api.api import Server
from task.task import TaskProcess

if __name__ == '__main__':
    server = Server()
    server.start()
    task = TaskProcess()
    task.start()
    while True:
        time.sleep(1)
