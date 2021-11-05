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


# https://github.com/jsvine/pdfplumber
def get_menu(date, when):
    database = Database()
    _attachment = list()

    if when in {'breakfast', '아침', '조식'}:
        data = database.select(date)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '조식'
        _json['text'] = data[Database.BREAKFAST]
        _attachment.append(_json)

    elif when in {'lunch', '점심', '중식'}:
        data = database.select(date)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 A코너'
        _json['text'] = data[Database.LUNCH_A]
        _attachment.append(_json)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 B코너'
        _json['text'] = data[Database.LUNCH_B]
        _attachment.append(_json)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 김치&샐러드'
        _json['text'] = data[Database.LUNCH_SIDE]
        _attachment.append(_json)
        if data[Database.LUNCH_SALAD]:
            _json = OrderedDict()
            _json['color'] = COLOR
            _json['author_name'] = '중식 SALAD BOX'
            _json['text'] = data[Database.LUNCH_SALAD]
            _attachment.append(_json)

    elif when in {'dinner', '저녁', '석식'}:
        data = database.select(date)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '석식'
        _json['text'] = data[Database.DINNER]
        _attachment.append(_json)

    elif when in {'today', '오늘'}:
        for _menu in get_menu(date, 'breakfast'):
            _attachment.append(_menu)
        for _menu in get_menu(date, 'lunch'):
            _attachment.append(_menu)
        for _menu in get_menu(date, 'dinner'):
            _attachment.append(_menu)

    else:
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '올바른 [when]을 입력해주세요.'
        _json['text'] = 'breakfast, 아침, 조식\n' \
                        'lunch, 점심, 중식\n' \
                        'dinner, 저녁, 석식\n' \
                        'today, 오늘\n' \
                        'tomorrow, 내일\n' \
                        'tomorrow breakfast, 내일 아침\n' \
                        'tomorrow lunch, 내일 점심\n' \
                        'tomorrow dinner, 내일 저녁'
        _attachment.append(_json)

    return _attachment


def logging(msg):
    with open("log.txt", "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        date = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime())
        log = '{date} {msg}'.format(date=date, msg=msg)
        file_object.write(log)
        usage.update(log)


def work():
    schedule.every().day.at("07:30").do(downloader.download_month)

    # downloader.download_month()
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

    date = datetime.datetime.today().strftime("%Y-%m-%d")
    if is_tomorrow(when):
        date = datetime.date.today() + datetime.timedelta(days=1)
        date = date.strftime("%Y-%m-%d")
        if len(subtract_tomorrow(when)) > 0:
            when = subtract_tomorrow(when)
        else:
            when = 'today'
    elif is_today(when) and len(subtract_today(when)) > 0:
        when = subtract_today(when)

    print('date={date}, when={when}'.format(date=date, when=when))
    menu = get_menu(date, when)

    _json = OrderedDict()
    _json['response_type'] = 'in_channel'
    _json['text'] = '판교세븐벤처밸리 {year}년 {month}월 {day}일'.format(
        year=date[:4],
        month=date[5:7],
        day=date[8:])
    _json['attachments'] = menu

    return _json


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
