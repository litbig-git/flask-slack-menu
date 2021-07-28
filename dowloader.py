import datetime
import os
import sys
import pdfplumber
import requests

path = './menu'
pvv_head = 'http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01'
pvv_id = 569


def is2021(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return pdf.pages[0].extract_text().count('Take Out') == 1


def find_keyword(pdf_file, keyword):
    with pdfplumber.open(pdf_file) as pdf:
        return keyword in pdf.pages[0].extract_text()


def download_pdf(month, weekday_of_month, init_duplicate):
    duplicate = init_duplicate

    while duplicate >= 0:
        pvv_filename_form = [
            '%02d' % month,
            '%02d' % weekday_of_month,
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

        if os.path.getsize(pdf_file_path) < 1000 \
                or is2021(pdf_file_path) is False:
            os.remove(pdf_file_path)

        if os.path.exists(pdf_file_path):
            print('new pdf file = {}'.format(pdf_file_path))
            break

        duplicate -= 1


# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=569&filename=판교07월04주(2).pdf
# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=569&filename=%C6%C7%B1%B307%BF%F904%C1%D6(2).pdf

def download_year():
    for month in range(3, 13):
        for weekday in range(1, 7):
            download_pdf(month, weekday, 15)


def download_month():
    for weekday in range(1, 7):
        download_pdf(datetime.datetime.today().month, weekday, 15)


def download_specific(month, weekday):
    download_pdf(month, weekday, 15)


if __name__ == '__main__':
    arg = sys.argv
    del arg[0]
    print('arg = {}'.format(arg))
    if len(arg) == 0:
        exit(-1)

    cmd = arg[0]

    if cmd == 'year':
        download_year()

    elif cmd == 'month':
        download_year()

    elif cmd == 'specific':
        if len(arg) < 3:
            exit(-1)

        month = int(arg[1])
        weekday = int(arg[2])
        download_specific(month, weekday)
