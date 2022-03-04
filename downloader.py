# -*- coding: utf-8 -*-

import datetime
import os
import sys
from pathlib import Path
import pdfplumber
import requests
import database

path = './menu'
pvv_head = 'http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01'
pvv_id = 569

# https://github.com/jsvine/pdfplumber


def is2021(_pdf_file):
    try:
        with pdfplumber.open(_pdf_file) as pdf:
            if len(pdf.pages) < 1:
                return False
            return pdf.pages[0].extract_text().count('Take Out') == 1
    except:
        print('open fail {}'.format(_pdf_file))
        return False


def find_keyword(_pdf_file, _keyword):
    with pdfplumber.open(_pdf_file) as pdf:
        return _keyword in pdf.pages[0].extract_text()


def download_pdf(_month, _weekday_of_month, _init_duplicate):
    Path(path).mkdir(parents=True, exist_ok=True)

    duplicate = _init_duplicate

    while duplicate >= 0:
        pvv_filename_form = [
            '%02d' % _month,
            '%02d' % _weekday_of_month,
            '({})'.format(duplicate) if duplicate != 0 else '',
            '.pdf'
        ]
        pvv_filename = '%C6%C7%B1%B3{month}%BF%F9{week_of_month}%C1%D6{duplicate}{extension}'.format(
            month=pvv_filename_form[0],
            week_of_month=pvv_filename_form[1],
            duplicate=pvv_filename_form[2],
            extension=pvv_filename_form[3]
        )
        pvv_filename_kor = '판교{month}월{week_of_month}주{extension}'.format(
            month=pvv_filename_form[0],
            week_of_month=pvv_filename_form[1],
            extension=pvv_filename_form[3]
        )

        url = '{head}&id={id}&filename={filename}'.format(
            head=pvv_head,
            id=pvv_id,
            filename=pvv_filename
        )
        r = requests.get(url, allow_redirects=True)
        pdf_file_path = '{}/{}'.format(path, pvv_filename_kor)
        pdf_file = open(pdf_file_path, 'wb')
        pdf_file.write(r.content)

        if os.path.exists(pdf_file_path) and Path(pdf_file_path).is_file() and \
                (os.path.getsize(pdf_file_path) < 1000 or is2021(pdf_file_path) is False):
            try:
                os.remove(pdf_file_path)
            except FileNotFoundError:
                print('FileNotFoundError {}'.format(pdf_file_path))

        if os.path.exists(pdf_file_path):
            print('new pdf file = {}'.format(pdf_file_path))
            break

        duplicate -= 1


# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=569&filename=판교07월04주(2).pdf
# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=569&filename=%C6%C7%B1%B307%BF%F904%C1%D6(2).pdf

def download_year():
    for _month in range(1, 13):
        for _weekday in range(1, 7):
            download_pdf(_month, _weekday, 15)
    database.database_update_all()
    print('download_year()')


def download_month():
    for _weekday in range(1, 7):
        download_pdf(datetime.datetime.today().month, _weekday, 15)
    database.database_update_all()
    print('download_month()')


def download_specific(_month, _weekday):
    download_pdf(_month, _weekday, 15)
    database.database_update_all()
    print('download_specific({month}, {weekday})'.format(month=_month, weekday=_weekday))


if __name__ == '__main__':
    arg = sys.argv
    del arg[0]
    print('arg = {}'.format(arg))
    if len(arg) == 0:
        exit(-1)

    cmd = arg[0]
    print('cmd={}'.format(cmd))

    if cmd == 'year':
        download_year()

    elif cmd == 'month':
        download_month()

    elif cmd == 'specific':
        if len(arg) < 3:
            exit(-1)

        month = int(arg[1])
        weekday = int(arg[2])
        download_specific(month, weekday)
