import datetime

import pdfplumber
from flask import Flask, request

import file

pdf_file = file.get_file()


# https://github.com/jsvine/pdfplumber
def get_menu(when):
    with pdfplumber.open(pdf_file) as pdf:
        first_page = pdf.pages[0]
        table = first_page.extract_table()
        weekday = datetime.datetime.today().weekday()

        if when in {'breakfast', '아침'}:
            menu = table[1][2 + weekday]

        elif when in {'lunch', '점심'}:
            menu = ''
            for r in range(2, 6):
                menu += '--{}--\n{}\n\n'.format(table[r][1], table[r][2 + weekday])

        elif when in {'dinner', '저녁'}:
            menu = ''
            for r in range(6, 9):
                menu += table[r][2 + weekday] + '\n'

        # print(menu)
        return menu


# https://hojak99.tistory.com/554
# https://cholol.tistory.com/421
# https://justkode.kr/python/flask-restapi-1
app = Flask(__name__)


@app.route('/menu', methods=['POST'])
def post():
    select = request.form['text']
    menu = get_menu(select)
    print('menu={}'.format(select))
    return {
        'response_type': 'in_channel',
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': '판교세븐벤처밸리 {}'.format(pdf_file.split('menu/')[1].split('.pdf')[0]),
                'author_name': select,
                'text': menu
            }
        ]
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
