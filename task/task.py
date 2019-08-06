#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 12:47
# @Author  : 项峥

import multiprocessing
import time

import requests
import schedule

from common.log import Log
from common.mysql import Mysql
from conf.conf import conf


class TaskProcess(multiprocessing.Process):
    def __init__(self):
        super(TaskProcess, self).__init__()
        Log.info("Task process init.")

    def run(self):
        schedule.every(conf['TASK_INTERVAL']['GET_NEW_DATA']).seconds.do(get_new_data)
        schedule.every(conf['TASK_INTERVAL']['COPY_IMPORTANT_DATA']).seconds.do(copy_important_data)
        while True:
            schedule.run_pending()
            time.sleep(1)


def get_new_data():
    # get data
    try:
        rsp = requests.get('http://localhost:5000/producer/data')
    except Exception as e:
        Log.error("ask api for new data error[{}]".format(str(e)))
        return
    if rsp.status_code != 200:
        Log.error("get data error[{}]".format(rsp.text))
        return
    result = rsp.json()
    if result['Code'] != 200:
        Log.error("get data error[{}]".format(result['Message']))
        return

    # insert data
    value_list = []
    for item in result['Data']['DataList']:
        value = "({Data1},{Data2},{Data3},{Data4},now())".format(Data1=item['Data1'], Data2=item['Data2'],
                                                                 Data3=item['Data3'], Data4=item['Data4'])
        value_list.append(value)
    db_conf = conf['DATABASE']
    mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
    result = mysql.connect()
    if result['code'] != 0:
        Log.error(result['info'])
        return
    # if the data is large, segmentation is required
    sql = "insert into table_1(data1,data2,data3,data4,created_time) values" + ','.join(value_list)
    result = mysql.write(sql)
    if result['code'] != 0:
        Log.error(result['info'])


def copy_important_data():
    # connect
    db_conf = conf['DATABASE']
    mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
    result = mysql.connect()
    if result['code'] != 0:
        Log.error(result['info'])
        return

    # detect data to copy
    sql = "select id from table_1 where flag = 1 order by id desc limit 1"
    result = mysql.read(sql)
    if result['code'] != 0:
        Log.error(result['info'])
        return
    if len(result['data']) == 0:
        return
    max_important_id_1 = result['data'][0]['id']
    sql = "select original_id from table_2 order by original_id desc limit 1"
    result = mysql.read(sql)
    if result['code'] != 0:
        Log.error(result['info'])
        return
    if len(result['data']) == 0:
        max_important_id_2 = 0
    else:
        max_important_id_2 = result['data'][0]['original_id']
    if max_important_id_1 == max_important_id_2:
        return
    elif max_important_id_1 < max_important_id_2:
        Log.error('table 1 data is abnormal.')
        return
    else:
        # start to copy
        sql = "select * from table_1 where id > {id} and flag = 1".format(id=max_important_id_2)
        result = mysql.read(sql)
        if result['code'] != 0:
            Log.error(result['info'])
            return
        # insert data
        value_list = []
        for item in result['data']:
            value = "({id},{data1},{data2},{data3},{data4},{flag},'{created_time}',now())".format(id=item['id'],
                                                                                                  data1=item['data1'],
                                                                                                  data2=item['data2'],
                                                                                                  data3=item['data3'],
                                                                                                  data4=item['data4'],
                                                                                                  flag=item['flag'],
                                                                                                  created_time=item[
                                                                                                      'created_time'])
            value_list.append(value)
        # if the data is large, segmentation is required
        sql = "insert into table_2(original_id,data1,data2,data3,data4,flag,original_created_time,created_time) values" + ','.join(
            value_list)
        result = mysql.write(sql)
        if result['code'] != 0:
            Log.error(result['info'])


if __name__ == '__main__':
    task_process = TaskProcess()
    task_process.start()
