import datetime
import os
import sys

import pymysql

sentence = 'form=ImmutableMultiDict'


class Database:
    DT = 'dt'
    TOKEN = 'token'
    TEAM_ID = 'team_id'
    TEAM_DOMAIN = 'team_domain'
    CHANNEL_ID = 'channel_id'
    CHANNEL_NAME = 'channel_name'
    USER_ID = 'user_id'
    USER_NAME = 'user_name'
    COMMAND = 'command'
    TEXT = 'text'
    API_APP_ID = 'api_app_id'
    IS_ENTERPRISE_INSTALL = 'is_enterprise_install'
    RESPONSE_URL = 'response_url'
    TRIGGER_ID = 'trigger_id'

    key_list = {DT, TOKEN, TEAM_ID, TEAM_DOMAIN, CHANNEL_ID, CHANNEL_NAME, USER_ID, USER_NAME,
                COMMAND, TEXT, API_APP_ID, IS_ENTERPRISE_INSTALL, RESPONSE_URL, TRIGGER_ID}

    USER = os.environ['RDS_USER']
    PASSWD = os.environ['RDS_PASSWD']
    HOST = 'database-menu-instance-1.chypan0rbkuk.ap-northeast-2.rds.amazonaws.com'
    PORT = 3306
    CHARSET = 'utf8'
    DB = 'menu'
    TABLE = 'table_usage'

    def __init__(self):
        self.create()

    def create(self):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                CREATE TABLE IF NOT EXISTS {table} (
                dt DATETIME PRIMARY KEY,
                token TEXT(50),
                team_id TEXT(50),
                team_domain TEXT(50),
                channel_id TEXT(50),
                channel_name TEXT(50),
                user_id TEXT(50),
                user_name TEXT(50),
                command TEXT(10),
                text TEXT(10),
                api_app_id TEXT(50),
                is_enterprise_install TEXT(10),
                response_url TEXT(500),
                trigger_id TEXT(500))
                '''.format(table=self.TABLE)
                cursor.execute(sql)

    def select(self, dt: str):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                SELECT * FROM {table} WHERE dt=%s
                '''.format(table=self.TABLE)
                cursor.execute(sql, dt)
                ret = cursor.fetchall()
                print('select={}'.format(ret))
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
                INSERT INTO {table} (
                dt, token, team_id, team_domain, channel_id, channel_name, user_id,
                user_name, command, text, api_app_id, is_enterprise_install, response_url, trigger_id)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''.format(table=self.TABLE)
                cursor.execute(sql, (model[self.DT],
                                     model[self.TOKEN],
                                     model[self.TEAM_ID],
                                     model[self.TEAM_DOMAIN],
                                     model[self.CHANNEL_ID],
                                     model[self.CHANNEL_NAME],
                                     model[self.USER_ID],
                                     model[self.USER_NAME],
                                     model[self.COMMAND],
                                     model[self.TEXT],
                                     model[self.API_APP_ID],
                                     model[self.IS_ENTERPRISE_INSTALL],
                                     model[self.RESPONSE_URL],
                                     model[self.TRIGGER_ID]))
                conn.commit()

    def update(self, model: dict):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                UPDATE {table}
                SET token=%s, team_id=%s, team_domain=%s, channel_id=%s, channel_name=%s, user_id=%s, user_name=%s,
                command=%s, text=%s, api_app_id=%s, is_enterprise_install=%s, response_url=%s, trigger_id=%s
                WHERE dt=%s
                '''.format(table=self.TABLE)
                cursor.execute(sql, (model[self.TOKEN],
                                     model[self.TEAM_ID],
                                     model[self.TEAM_DOMAIN],
                                     model[self.CHANNEL_ID],
                                     model[self.CHANNEL_NAME],
                                     model[self.USER_ID],
                                     model[self.USER_NAME],
                                     model[self.COMMAND],
                                     model[self.TEXT],
                                     model[self.API_APP_ID],
                                     model[self.IS_ENTERPRISE_INSTALL],
                                     model[self.RESPONSE_URL],
                                     model[self.TRIGGER_ID],
                                     model[self.DT]))
                conn.commit()

    def delete(self, dt: str):
        with pymysql.connect(user=self.USER, passwd=self.PASSWD, host=self.HOST, port=self.PORT, db=self.DB) as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = '''
                DELETE FROM {table} WHERE dt=%s
                '''.format(table=self.TABLE)
                cursor.execute(sql, dt)
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
            conn.execute('SELECT * FROM {table} ORDER BY {primary_key}'.format(table=self.TABLE, primary_key=self.DT))


def update_all(file_name: str):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        db = Database()

        for line in lines:
            line = line.strip()

            if len('line={}'.format(line)) < 544:
                continue

            a = line[1:20].split(' ')
            if len(a) != 2:
                continue

            date = list(map(int, a[0].split('-')))
            time = list(map(int, a[1].split(':')))
            if len(date) != 3 or len(time) != 3:
                continue

            dt = datetime.datetime(date[0], date[1], date[2], time[0], time[1], time[2])
            pos = line.find(sentence) + len(sentence)
            values = dict(eval(line[pos:]))
            values[Database.DT] = dt

            db.update(values) if db.select(values[Database.DT]) else db.insert(values)
        db.order()


def update(line: str):
    db = Database()

    if len('line={}'.format(line)) < 544:
        return

    a = line[1:20].split(' ')
    if len(a) != 2:
        return

    date = list(map(int, a[0].split('-')))
    time = list(map(int, a[1].split(':')))
    if len(date) != 3 or len(time) != 3:
        return

    dt = datetime.datetime(date[0], date[1], date[2], time[0], time[1], time[2])
    pos = line.find(sentence) + len(sentence)
    values = dict(eval(line[pos:]))
    values[Database.DT] = dt

    db.update(values) if db.select(values[Database.DT]) else db.insert(values)


if __name__ == '__main__':
    arg = sys.argv
    del arg[0]
    print('arg = {}'.format(arg))
    if len(arg) == 0:
        exit(-1)

    cmd = arg[0]
    db = Database()

    if cmd == 'update_all':
        update_all('log.txt')

    elif cmd == 'select':
        db.select('2021-11-03 17:41:10')

    elif cmd == 'delete_all':
        db.delete_all()

    elif cmd == 'order':
        db.order()
