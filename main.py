import datetime
from collections import OrderedDict
from flask import Flask, request
from database import Database

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
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '조식'
        _json['text'] = database.select(date)[Database.BREAKFAST]
        _attachment.append(_json)

    elif when in {'lunch', '점심', '중식'}:
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 A코너'
        _json['text'] = database.select(date)[Database.LUNCH_A]
        _attachment.append(_json)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 B코너'
        _json['text'] = database.select(date)[Database.LUNCH_B]
        _attachment.append(_json)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 김치&샐러드'
        _json['text'] = database.select(date)[Database.LUNCH_SIDE]
        _attachment.append(_json)
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '중식 SALAD BOX'
        _json['text'] = database.select(date)[Database.LUNCH_SALAD]
        _attachment.append(_json)

    elif when in {'dinner', '저녁', '석식'}:
        _json = OrderedDict()
        _json['color'] = COLOR
        _json['author_name'] = '석식'
        _json['text'] = database.select(date)[Database.DINNER]
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


# https://hojak99.tistory.com/554
# https://cholol.tistory.com/421
# https://justkode.kr/python/flask-restapi-1
app = Flask(__name__)


@app.route('/menu', methods=['POST'])
def post():
    when: str = ''
    print('len(form)={}'.format(len(request.form)))
    print('len(json)={}'.format(len(request.json)))
    if len(request.form) > 0:
        print('form')
        when = request.form['text']
    elif len(request.json) > 0:
        print('json')
        when = request.json['text']

    print('when={}'.format(when))

    date = datetime.datetime.today().strftime("%Y%m%d")
    if is_tomorrow(when):
        date = datetime.date.today() + datetime.timedelta(days=1)
        date = date.strftime("%Y%m%d")
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
        month=date[4:6],
        day=date[6:])
    _json['attachments'] = menu

    return _json


if __name__ == '__main__':
    app.run(debug=True, port=5001)
