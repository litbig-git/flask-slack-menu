import datetime
import os

import requests

path = './menu'
pvv_head = 'http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01'
pvv_id = 569
pvv_filename_form = ['%02d' % datetime.date.today().month, '02', '.pdf']
pvv_filename = '%C6%C7%B1%B3{}%BF%F9{}%C1%D6{}'.format(pvv_filename_form[0], pvv_filename_form[1], pvv_filename_form[2])
pvv_filename_kor = '판교{}월{}주{}'.format(pvv_filename_form[0], pvv_filename_form[1], pvv_filename_form[2])

url = '{}&id={}&filename={}'.format(pvv_head, pvv_id, pvv_filename)
r = requests.get(url, allow_redirects=True)
pdf_file_path = '{}/{}'.format(path, pvv_filename_kor)
pdf_file = open(pdf_file_path, 'wb')
pdf_file.write(r.content)
if os.path.getsize(pdf_file_path) < 1000:
    os.remove(pdf_file_path)

print(datetime.date.today().month)


# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=568&filename=판교07월04주.pdf
# http://www.pvv.co.kr/bbs/download.php?bbsMode=fileDown&code=bbs_menu01&id=568&filename=%C6%C7%B1%B307%BF%F903%C1%D6.pdf

