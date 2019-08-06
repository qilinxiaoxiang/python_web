#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/07/11 12:12
# @Author  : 项峥
import datetime
import json
import random
import multiprocessing
from functools import wraps

from flask import Flask
from flask_restplus import Api, Resource, reqparse

from common.log import Log
from common.mysql import Mysql
from conf.conf import conf


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return super(Encoder, self).default(o)


app = Flask(__name__, template_folder='static')
api = Api(app)
app.json_encoder = Encoder
app.config['RESTPLUS_JSON'] = {'cls': app.json_encoder}


def success_response(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = f(*args, **kwargs)
        return {'Code': 200, 'Message': 'success', 'Data': data}, 200

    return wrapper


@api.route('/portal')
class Portal(Resource):
    def get(self):
        return app.send_static_file('portal.html')


@api.route('/producer/data')
class ProducerData(Resource):
    @success_response
    def get(self):
        counts = random.randint(20, 50)
        data_list = []
        for i in range(0, counts):
            data_list.append({
                'Data1': random.randint(1, 100),
                'Data2': random.randint(1, 100),
                'Data3': random.randint(1, 100),
                'Data4': random.randint(1, 100),
            })
        return {'DataList': data_list}


@api.route('/current/data')
class CurrentData(Resource):
    @success_response
    def get(self):
        db_conf = conf['DATABASE']
        mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
        result = mysql.connect()
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        sql = "select id,data1,data2,data3,data4,created_time from table_1 where created_time + interval 10 second > now()"
        result = mysql.read(sql)
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        if len(result['data']) == 0:
            raise Exception('No data in recent 10 seconds.')
        data_list = []
        for item in result['data']:
            tmp = dict()
            tmp['Id'] = item['id']
            tmp['Data1'] = item['data1']
            tmp['Data2'] = item['data2']
            tmp['Data3'] = item['data3']
            tmp['Data4'] = item['data4']
            tmp['CreatedTime'] = item['created_time']
            data_list.append(tmp)
        return {'DataList': data_list}


@api.route('/current/data/flag')
class CurrentDataFlag(Resource):
    @success_response
    def put(self):
        # param check
        parser = reqparse.RequestParser()
        parser.add_argument('DataIds', required=True)
        args = parser.parse_args()
        data_ids = args.get('DataIds').strip()
        data_id_list = data_ids.split(',')
        if len(data_id_list) == 0:
            raise Exception('Invalid DataIds')
        for data_id in data_id_list:
            if not data_id.isdigit():
                raise Exception('Invalid DataIds')

        # update the flag to 1, which means important
        db_conf = conf['DATABASE']
        mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
        result = mysql.connect()
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        data_ids = args.get('DataIds')
        sql = "update table_1 set flag = 1 where id in ({}) and flag = 0".format(data_ids)
        result = mysql.write(sql)
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        return {'DataIds': data_ids}


@api.route('/current/importData')
class CusrrentImportData(Resource):
    @success_response
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('PageSize', type=int)
        parser.add_argument('PageNo', type=int)
        args = parser.parse_args()
        page_size = args.get('PageSize')
        page_no = args.get('PageNo')
        if page_size is None:
            page_size = 100
        elif page_size <= 0:
            raise Exception('Invalid PageSize')
        if page_no is None:
            page_no = 1
        elif page_no <= 0:
            raise Exception('Invalid PageNo')

        db_conf = conf['DATABASE']
        mysql = Mysql(db_conf['HOST'], db_conf['PORT'], db_conf['USER'], db_conf['PASSWORD'], db_conf['DATABASE'])
        result = mysql.connect()
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        sql = "select count(*) from table_2"
        result = mysql.read(sql)
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        total_records = result['data'][0]['count(*)']
        offset = (page_no - 1) * page_size
        sql = "select data1,data2,data3,data4,original_created_time,original_id from table_2 order by id desc " \
              "limit {0},{1}".format(offset, page_size)
        result = mysql.read(sql)
        if result['code'] != 0:
            Log.error(result['info'])
            raise Exception(result['info'])
        if len(result['data']) == 0:
            raise Exception('No data in recent 10 seconds.')
        data_list = []
        for item in result['data']:
            tmp = dict()
            tmp['Data1'] = item['data1']
            tmp['Data2'] = item['data2']
            tmp['Data3'] = item['data3']
            tmp['Data4'] = item['data4']
            tmp['Id'] = item['original_id']
            tmp['CreatedTime'] = item['original_created_time']
            data_list.append(tmp)
        rsp = dict()
        rsp['DataList'] = data_list
        rsp['PageSize'] = page_size
        rsp['PageNo'] = page_no
        rsp['TotalRecords'] = total_records
        return rsp


class Server(multiprocessing.Process):
    def __init__(self):
        super(Server, self).__init__()
        Log.info("Server init")

    def run(self):
        app.run(port=conf['SERVER']['PORT'])


if __name__ == '__main__':
    server = Server()
    server.start()
