#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 12:11
# @Author  : 项峥
import time

import pymysql

from common.result import success_result, error_result
from conf.conf import conf


class Mysql(object):

    def __init__(self, host, port, user, password, database=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def connect(self, conn_timeout=0.5, read_timeout=5, write_timeout=5, max_retry_time=1):
        retry_index = 0
        e = None
        while retry_index < max_retry_time:
            retry_index = 1
            try:
                config = {
                    'host': self.host,
                    'port': int(self.port),
                    'user': self.user,
                    'password': self.password,
                    'database': self.database,
                    'connect_timeout': conn_timeout * retry_index,
                    'read_timeout': read_timeout * retry_index,
                    'write_timeout': write_timeout * retry_index,
                    'charset': 'utf8',
                    'cursorclass': pymysql.cursors.DictCursor,
                    'autocommit': True
                }
                self.conn = pymysql.connect(**config)
                return success_result()
            except Exception as e:
                time.sleep(0.1)
                continue
        return error_result("mysql_conn error[{}]".format(str(e)))

    def read(self, sql):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            result_data = []
            for line in rows:
                result_data.append(line)
            return success_result(result_data)
        except Exception as e:
            return error_result("mysql_read error[{}]".format(str(e)))

    def write(self, sql):
        try:
            cur = self.conn.cursor()
            row_count = cur.execute(sql)
            cur.close()
            return success_result({"affected_rows": row_count})
        except Exception as e:
            return error_result("mysql_write error[{}]".format(str(e)))

    def close(self):
        try:
            self.conn.close()
            return success_result()
        except Exception as e:
            return error_result("close mysql_conn error[{}]".format(str(e)))


if __name__ == '__main__':
    db_conf = conf['DATABASE']
    mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
    result = mysql.connect()
    print(result)