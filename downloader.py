# -*- coding: utf-8 -*-

import os.path
import time
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import database

id_file = 'id.txt'


def set_id(id):
    f = open(id_file, 'w')
    f.write(str(id))
    f.close()


def get_id():
    f = open(id_file, 'r')
    data = f.read()
    f.close()
    return int(data)


def inc_id():
    f = open(id_file, 'r+')
    data = int(f.read())
    print(data)
    f.seek(0)
    f.write(str(data + 1))
    f.close()


def init_id():
    if not os.path.exists(id_file) or os.path.getsize(id_file) < 1:
        print('no file')
        set_id(600)


# pvv_id
# 2020년 488 ~ 539
# 2021년 540 ~ 591
# 2022년 592 ~
def download_pdf(pvv_id) -> str:
    path = './menu'
    pvv_head = 'http://www.pvv.co.kr/bbs/'
    html = urlopen(pvv_head + 'bbsView.php?id={id}&page=1&code=bbs_menu01'.format(id=pvv_id))

    # 웹크롤링 https://webnautes.tistory.com/779
    js_code = str(BeautifulSoup(html, "html.parser"))
    start, end = js_code.rfind('download.php?bbsMode=fileDown'), js_code.rfind('.pdf"')
    if start < 0 or end < 0:
        print('게시글이 없습니다.')
        return ''
    else:
        inc_id()

    file_link = js_code[start:end + 4]

    if pvv_id <= 539:
        year = 2020
    elif pvv_id <= 591:
        year = 2021
    else:
        year = 2022
    file_name = file_link[file_link.find('판교'):]
    bracket = file_name[file_name.find('('):file_name.find(')') + 1]
    file_name = file_name.replace(bracket, '')
    file_name = '{year}년{file}'.format(year=year, file=file_name)
    print('파일이름={}'.format(file_name))

    file_link = file_link \
        .replace('&amp;', '&') \
        .replace('판교', '%C6%C7%B1%B3') \
        .replace('월', '%BF%F9') \
        .replace('주', '%C1%D6')
    download_link = pvv_head + file_link
    print('url={}'.format(download_link))

    r = requests.get(download_link, allow_redirects=True)
    pdf_file_path = '{}/{}'.format(path, file_name)
    pdf_file = open(pdf_file_path, 'wb')
    pdf_file.write(r.content)

    return file_name


def periodical_download():
    init_id()
    while True:
        file_name = download_pdf(get_id())

        if file_name is None or not file_name:
            break
        time.sleep(1)
    database.database_update_all()


if __name__ == '__main__':
    periodical_download()
