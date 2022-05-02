# -*- coding: utf-8 -*-

import datetime
import threading
from collections import OrderedDict
import schedule
from flask import Flask, request
import downloader
import usage
from database import Database
import time
from block import Block

COLOR = '#ffce30'


def is_today(when: str):
    tomorrow_list = {'today', '오늘'}
    ret: bool = False
    for tomorrow in tomorrow_list:
        if tomorrow in when:
            ret = True
            break
    return ret


def subtract_today(when: str):
    today_list = {'today', '오늘'}
    ret: str = ''
    for today in today_list:
        if today in when:
            ret = when.replace(today, '').replace(' ', '')
            break
    return ret


def is_tomorrow(when: str):
    tomorrow_list = {'tomorrow', '내일'}
    ret: bool = False
    for tomorrow in tomorrow_list:
        if tomorrow in when:
            ret = True
            break
    return ret


def subtract_tomorrow(when: str):
    tomorrow_list = {'tomorrow', '내일'}
    ret: str = ''
    for tomorrow in tomorrow_list:
        if tomorrow in when:
            ret = when.replace(tomorrow, '').replace(' ', '')
            break
    return ret


database = Database()
block = Block()


# https://app.slack.com/block-kit-builder
def get_block(date: datetime, when, db: Database, is_header: bool = True):
    data = db.select(date.strftime("%Y-%m-%d"))

    _json = list()

    if data is None:
        _json += block.get_header(date, "메뉴가 없어요 :(")
        return _json

    if is_header:
        _json += block.get_header(date, "요청하신 메뉴를 알려드릴게요 :)")

    if when in {'breakfast', '아침', '조식'}:
        _json += block.get_divider()
        _json += block.get_menu("bread", "아침", data[Database.BREAKFAST])

    elif when in {'lunch', '점심', '중식'}:
        _json += block.get_divider()
        _json += block.get_menu("spaghetti", "점심 A코너", data[Database.LUNCH_A])
        _json += block.get_menu("rice", "점심 B코너", data[Database.LUNCH_B])
        _json += block.get_menu("leafy_green", "김치&샐러드", data[Database.LUNCH_SIDE])
        _json += block.get_menu("green_salad", "SALAD BOX", data[Database.LUNCH_SALAD])

    elif when in {'dinner', '저녁', '석식'}:
        _json += block.get_divider()
        _json += block.get_menu("beer", "저녁", data[Database.DINNER])

    elif when in {'today', '오늘'}:
        _json += get_block(date, 'breakfast', db, False)
        _json += get_block(date, 'lunch', db, False)
        _json += get_block(date, 'dinner', db, False)

    else:
        _json.clear()
        _json += block.get_header(date, "올바른 [when]을 입력해주세요 :(")
        _json += block.get_divider()
        _json += block.get_menu("bread", "breakfast, 아침, 조식")
        _json += block.get_menu("spaghetti", "lunch, 점심, 중식")
        _json += block.get_menu("beer", "dinner, 저녁, 석식")
        _json += block.get_menu("pizza", "today, 오늘")
        _json += block.get_menu("fries", "tomorrow, 내일")
        _json += block.get_menu("fried_shrimp", "tomorrow breakfast, 내일 아침")
        _json += block.get_menu("fried_egg", "tomorrow lunch, 내일 점심")
        _json += block.get_menu("sandwich", "tomorrow dinner, 내일 저녁")

    return _json


def logging(msg):
    date = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())
    log = '{date} {msg}'.format(date=date, msg=msg)
    usage.update(log)


def work():
    schedule.every().monday.at("06:00").do(downloader.periodical_download)

    downloader.periodical_download()
    while True:
        schedule.run_pending()
        time.sleep(1)


class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug:
            with self.app_context():
                thread = threading.Thread(target=work)
                thread.daemon = True
                thread.start()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


# https://hojak99.tistory.com/554
# https://cholol.tistory.com/421
# https://justkode.kr/python/flask-restapi-1
app = MyFlaskApp(__name__)


@app.route('/menu', methods=['POST'])
def post():
    when: str = ''

    if request.form is not None and len(request.form) > 0:
        print('form={}'.format(request.form))
        logging('form={}'.format(request.form))
        when = request.form['text']
    elif request.json is not None and len(request.json) > 0:
        print('json={}'.format(request.json))
        logging('json={}'.format(request.json))
        when = request.json['text']

    date = datetime.datetime.today()
    if is_tomorrow(when):
        date += datetime.timedelta(days=1)

        if len(subtract_tomorrow(when)) > 0:
            when = subtract_tomorrow(when)
        else:
            when = 'today'
    elif is_today(when) and len(subtract_today(when)) > 0:
        when = subtract_today(when)

    print('date={date}, when={when}'.format(date=date.strftime("%Y-%m-%d"), when=when))
    menu = get_block(date, when, database)

    _json = OrderedDict()
    _json['response_type'] = 'in_channel'
    _json['blocks'] = menu

    return _json


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
