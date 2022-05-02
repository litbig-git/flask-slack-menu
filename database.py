# -*- coding: utf-8 -*-

import datetime
import os
import re
import sys

import pdfplumber
import pymysql
from collections import defaultdict


class Database:
    DATE = 'date'
    BREAKFAST = 'breakfast'
    LUNCH_A = 'lunch_a'
    LUNCH_B = 'lunch_b'
    LUNCH_SIDE = 'lunch_side'
    LUNCH_SALAD = 'lunch_salad'
    DINNER = 'dinner'

    key_list = {DATE, BREAKFAST, LUNCH_A, LUNCH_B, LUNCH_SIDE, LUNCH_SALAD, DINNER}

    USER = os.environ['RDS_USER']
    PASSWD = os.environ['RDS_PASSWD']
    HOST = 'database-mysql.chypan0rbkuk.ap-northeast-2.rds.amazonaws.com'
    PORT = 3306
    CHARSET = 'utf8'
    DB = 'menu'
    TABLE = 'table_menu'

    def __init__(self):
        self.create()

    def create(self):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                CREATE TABLE IF NOT EXISTS {table} (
                date DATE PRIMARY KEY,
                breakfast TEXT(500),
                lunch_a TEXT(500),
                lunch_b TEXT(500),
                lunch_side TEXT(500),
                lunch_salad TEXT(500),
                dinner TEXT(500))
                '''.format(table=self.TABLE)
                cursor.execute(sql)

    def select(self, date: str):
        # print('date=' + date)
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                SELECT * FROM {table} WHERE date=%s
                '''.format(table=self.TABLE)
                cursor.execute(sql, date)
                ret = cursor.fetchone()
                #print('select={}'.format(ret))
                return ret

    def select_all(self):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                SELECT * FROM {table}
                '''.format(table=self.TABLE)
                cursor.execute(sql)
                ret = cursor.fetchall()
                print('select={}'.format(ret))
                return ret

    def insert(self, model: dict):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                INSERT INTO {table}(date, breakfast, lunch_a, lunch_b, lunch_side, lunch_salad, dinner) 
                VALUES(%s,%s,%s,%s,%s,%s,%s)
                '''.format(table=self.TABLE)
                cursor.execute(sql, (model[self.DATE],
                                     model[self.BREAKFAST],
                                     model[self.LUNCH_A],
                                     model[self.LUNCH_B],
                                     model[self.LUNCH_SIDE],
                                     model[self.LUNCH_SALAD],
                                     model[self.DINNER]))
                conn.commit()

    def update(self, model: dict):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                UPDATE {table} 
                SET breakfast=%s, lunch_a=%s, lunch_b=%s, lunch_side=%s, lunch_salad=%s, dinner=%s 
                WHERE date=%s'''.format(table=self.TABLE)
                cursor.execute(sql, (model[self.BREAKFAST],
                                     model[self.LUNCH_A],
                                     model[self.LUNCH_B],
                                     model[self.LUNCH_SIDE],
                                     model[self.LUNCH_SALAD],
                                     model[self.DINNER],
                                     model[self.DATE]))
                conn.commit()

    def delete(self, date: str):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                DELETE FROM {table} WHERE date=%s
                '''.format(table=self.TABLE)
                cursor.execute(sql, (date,))
                conn.commit()

    def delete_all(self):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                TRUNCATE {table}
                '''.format(table=self.TABLE)
                cursor.execute(sql)

    def order(self):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute('SELECT * FROM {table} ORDER BY {primary_key}'.format(table=self.TABLE, primary_key=self.DATE))


def list_up_menu():
    _menu_list = list()

    path = './menu'
    for file in sorted(os.listdir(path)):
        if not file.endswith('.pdf'):
            continue
        file = path + '/' + file
        print(file)
        with pdfplumber.open(file) as pdf:
            first_page = pdf.pages[0]
            table = first_page.extract_table()

            row = len(table)
            # print('================row={}'.format(row))

            for weekday in range(0, 5):
                _menu = defaultdict(str)
                _menu[Database.DATE] = '{year}{month_day}'.format(
                    year='%d' % datetime.datetime.today().year,
                    month_day=re.sub(r'[^0-9]', '', table[0][2 + weekday])
                )
                # print('\n>>>DATE={}'.format(_menu[Database.DATE]))
                for r in range(1, row):
                    value = table[r][2 + weekday]
                    if value is None or len(value) == 0:
                        continue

                    a = table[r][0].replace('\n', '').replace(' ', '').upper() if table[r][0] is not None else ''
                    b = table[r][1].replace('\n', '').replace(' ', '').upper() if table[r][1] is not None else ''
                    # print('r={}, a={}, b={}, value={}'.format(r, a, b, value))
                    if '조식' in a or '한식' in b:
                        _menu[Database.BREAKFAST] = value
                        # print('>>>BREAKFAST={}'.format(_menu[Database.BREAKFAST]))
                    elif 'A코너' in b or r == 2:
                        if len(_menu[Database.LUNCH_A]) == 0:
                            _menu[Database.LUNCH_A] = value
                        else:
                            _menu[Database.LUNCH_A] += value
                        # print('>>>LUNCH_A={}'.format(_menu[Database.LUNCH_A]))
                    elif 'B코너' in b:
                        _menu[Database.LUNCH_B] = value
                        # print('>>>LUNCH_B={}'.format(_menu[Database.LUNCH_B]))
                    elif b in {'김치&샐러드', 'SALADBAR', '플러스코너'}:
                        _menu[Database.LUNCH_SIDE] = value
                        # print('>>>LUNCH_SIDE={}'.format(_menu[Database.LUNCH_SIDE]))
                    elif 'SALADBOX' in b:
                        _menu[Database.LUNCH_SALAD] = value
                        # print('>>>LUNCH_SALAD={}'.format(_menu[Database.LUNCH_SALAD]))
                    elif '석식' in a:
                        _menu[Database.DINNER] = value
                        # print('>>>DINNER={}'.format(_menu[Database.DINNER]))
                    elif 'TAKEOUT' in a:
                        print('>>>TAKEOUT={}'.format(value))
                    elif '이용가능' not in value:
                        _menu[Database.DINNER] += '\n' + value
                        # print('>>>DINNER={}'.format(_menu[Database.DINNER]))

                # print('_menu={}'.format(_menu))
                # print('len(_menu)={}'.format(len(_menu)))

                _menu_list.append(_menu)

    return _menu_list


def database_update_all():
    db = Database()
    for _menu in list_up_menu():
        db.update(_menu) if db.select(_menu[Database.DATE]) else db.insert(_menu)
    db.order()


def database_migrate(data_list):
    db = Database()
    for data in data_list:
        db.update(data) if db.select(data[Database.DATE]) else db.insert(data)
    db.order()


if __name__ == '__main__':
    arg = sys.argv
    del arg[0]
    print('arg = {}'.format(arg))
    if len(arg) == 0:
        exit(-1)

    cmd = arg[0]
    db = Database()

    if cmd == 'clear':
        db.delete_all()

    elif cmd == 'update':
        database_update_all()

    elif cmd == 'today':
        print(db.select(datetime.datetime.today().strftime('%Y%m%d')))

    elif cmd == 'select' and len(arg) >= 2:
        print(db.select(str(arg[1])))

    elif cmd == 'all':
        print(db.select_all())

    elif cmd == 'order':
        db.order()

    elif cmd == 'listup':
        for _menu in list_up_menu():
            print(_menu)
