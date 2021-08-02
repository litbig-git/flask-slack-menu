import datetime
from collections import OrderedDict
import pdfplumber
from flask import Flask, request
import file

color = '#ffce30'
pdf_file = file.get_file()


# https://github.com/jsvine/pdfplumber
def get_menu(when):
    with pdfplumber.open(pdf_file) as pdf:
        first_page = pdf.pages[0]
        table = first_page.extract_table()
        weekday = datetime.datetime.today().weekday()
        _attachment = list()

        if when in {'breakfast', '아침', '조식'}:
            _json = OrderedDict()
            _json['color'] = color
            _json['author_name'] = table[1][1]
            _json['text'] = table[1][2 + weekday]
            _attachment.append(_json)

        elif when in {'lunch', '점심', '중식'}:
            for r in range(2, 6):
                _json = OrderedDict()
                _json['color'] = color
                _json['author_name'] = table[r][1].replace('\n', '')
                _json['text'] = table[r][2 + weekday]
                _attachment.append(_json)

        elif when in {'dinner', '저녁', '석식'}:
            _json = OrderedDict()
            _json['color'] = color
            _json['author_name'] = table[6][1]
            row = len(table)
            if row == 9:
                _json['text'] = table[6][2 + weekday]
            else:
                _text = ''
                for r in range(6, 9):
                    _text += table[r][2 + weekday] + '\n'
                _json['text'] = _text
            _attachment.append(_json)

        else:
            _json = OrderedDict()
            _json['color'] = color
            _json['author_name'] = '올바른 [when]을 입력해주세요.'
            _json['text'] = 'breakfast, lunch, dinner\n아침, 점심, 저녁\n조식, 중식, 석식'
            _attachment.append(_json)

        # print(menu)
        return _attachment


# https://hojak99.tistory.com/554
# https://cholol.tistory.com/421
# https://justkode.kr/python/flask-restapi-1
app = Flask(__name__)


@app.route('/menu', methods=['POST'])
def post():
    select = request.form['text']
    menu = get_menu(select)
    print('select={}'.format(select))
    print('form={}'.format(request.form))

    _json = OrderedDict()
    _json['response_type'] = 'in_channel'
    _json['text'] = '판교세븐벤처밸리 {}월 {}일 {}'.format(
        datetime.datetime.today().month,
        datetime.datetime.today().day,
        select)
    _json['attachments'] = menu

    return _json


if __name__ == '__main__':
    app.run(debug=True, port=5001)
