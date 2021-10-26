import os
import re
import sqlite3
import datetime
import sys

import pdfplumber


class Menu:
    date: str
    breakfast: str
    lunch_a: str
    lunch_b: str
    lunch_side: str
    lunch_salad: str
    dinner: str

    def __init__(self):
        self.date = ''
        self.breakfast = ''
        self.lunch_a = ''
        self.lunch_b = ''
        self.lunch_side = ''
        self.lunch_salad = ''
        self.dinner = ''


# http://hleecaster.com/python-sqlite3/
class Database:
    DATE = 'date'
    BREAKFAST = 'breakfast'
    LUNCH_A = 'lunch_a'
    LUNCH_B = 'lunch_b'
    LUNCH_SIDE = 'lunch_side'
    LUNCH_SALAD = 'lunch_salad'
    DINNER = 'dinner'

    db = 'menu.db'
    table = 'table1'

    def __init__(self):
        self.create()

    def create(self):
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS {table} \
            (date text PRIMARY KEY, \
            breakfast text, \
            lunch_a text, \
            lunch_b text, \
            lunch_side text, \
            lunch_salad text, \
            dinner text)'.format(table=self.table))
        conn.close()

    def insert(self, model: Menu):
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('INSERT INTO {table}(date, breakfast, lunch_a, lunch_b, lunch_side, lunch_salad, dinner) \
                  VALUES(?,?,?,?,?,?,?)'.format(table=self.table), \
                  (model.date,
                   model.breakfast,
                   model.lunch_a,
                   model.lunch_b,
                   model.lunch_side,
                   model.lunch_salad,
                   model.dinner))
        conn.close()

    def select(self, date):
        # print('date=' + date)
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('SELECT * FROM {table} WHERE date=?'.format(table=self.table), (date,))
        ret = c.fetchone()
        conn.close()
        # if ret is None:
        #     ret = '없음'
        return ret

    def select_all(self):
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('SELECT * FROM {table}'.format(table=self.table))
        ret = c.fetchall()
        conn.close()
        return ret

    def update(self, model: Menu):
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('UPDATE {table} \
                    SET breakfast=?, lunch_a=?, lunch_b=?, lunch_side=?, lunch_salad=?, dinner=?\
                    WHERE date=?'.format(table=self.table),
                  (model.breakfast, model.lunch_a, model.lunch_b, model.lunch_side, model.lunch_salad, model.dinner,
                   model.date))
        conn.close()

    def delete(self, date):
        conn = sqlite3.connect(self.db, isolation_level=None)
        c = conn.cursor()
        c.execute('DELETE FROM {table} WHERE date=?'.format(table=self.table), (date,))
        conn.close()

    def delete_all(self):
        conn = sqlite3.connect(self.db, isolation_level=None)
        ret = conn.execute("DELETE FROM table1").rowcount
        conn.close()
        return ret


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
            # print('row={}'.format(row))

            for weekday in range(0, 5):
                _menu = Menu()
                _menu.date = '{year}{month_day}'.format(
                    year='%d' % datetime.datetime.today().year,
                    month_day=re.sub(r'[^0-9]', '', table[0][2 + weekday])
                )

                _list = dict()
                _list[Database.DATE] = _menu.date
                for r in range(1, row):
                    value = table[r][2 + weekday]
                    if value is None or len(value) == 0:
                        continue

                    a = table[r][0].replace('\n', '').replace(' ', '').upper() if table[r][0] is not None else ''
                    b = table[r][1].replace('\n', '').replace(' ', '').upper() if table[r][1] is not None else ''
                    if a == '조식' or b == '한식':
                        _list[Database.BREAKFAST] = value
                    elif a == '중식' or b == 'A코너':
                        _list[Database.LUNCH_A] = value
                    elif a == '중식' or b == 'B코너':
                        _list[Database.LUNCH_B] = value
                    elif b in {'김치&샐러드', 'SALADBAR', '플러스코너'}:
                        _list[Database.LUNCH_SIDE] = value
                    elif a == '중식' or b == 'SALADBOX':
                        _list[Database.LUNCH_SALAD] = value
                    elif a == '석식':
                        _list[Database.DINNER] = value

                # print(_list)
                # 10월04주부터 salad box 사라짐.
                if len(_list) == 6:
                    _menu.breakfast = _list[Database.BREAKFAST]
                    _menu.lunch_a = _list[Database.LUNCH_A]
                    _menu.lunch_b = _list[Database.LUNCH_B]
                    _menu.lunch_side = _list[Database.LUNCH_SIDE]
                    _menu.lunch_salad = '없음'
                    _menu.dinner = _list[Database.DINNER]
                elif len(_list) != 7:
                    _menu.breakfast = \
                        _menu.lunch_a = \
                        _menu.lunch_b = \
                        _menu.lunch_side = \
                        _menu.lunch_salad = \
                        _menu.dinner = '없음'
                else:
                    _menu.breakfast = _list[Database.BREAKFAST]
                    _menu.lunch_a = _list[Database.LUNCH_A]
                    _menu.lunch_b = _list[Database.LUNCH_B]
                    _menu.lunch_side = _list[Database.LUNCH_SIDE]
                    _menu.lunch_salad = _list[Database.LUNCH_SALAD]
                    _menu.dinner = _list[Database.DINNER]

                _menu_list.append(_menu)

    return _menu_list


def database_update_all():
    __database = Database()
    for _menu in list_up_menu():
        if __database.select(_menu.date):
            __database.update(_menu)
        else:
            __database.insert(_menu)


if __name__ == '__main__':
    arg = sys.argv
    del arg[0]
    print('arg = {}'.format(arg))
    if len(arg) == 0:
        exit(-1)

    cmd = arg[0]

    database = Database()

    if cmd == 'clear':
        database.delete_all()

    elif cmd == 'update':
        database_update_all()

    elif cmd == 'today':
        print(database.select(datetime.datetime.today().strftime('%Y%m%d')))

    elif cmd == 'select' and len(arg) >= 2:
        print(database.select(str(arg[1])))

    elif cmd == 'all':
        print(database.select_all())
