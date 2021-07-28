import os
import time

import schedule


def job():
    os.system('python3 downloader.py month')
    # print("I'm working...")


# 10초에 한번씩 실행
# schedule.every(1).second.do(job)
# 10분에 한번씩 실행
# schedule.every(10).minutes.do(job)
# 매 시간 실행
# schedule.every().hour.do(job)
# 매일 08:30 에 실행
schedule.every().day.at("08:30").do(job)
# 매주 월요일 실행
# schedule.every().monday.do(job)
# 매주 수요일 13:15 에 실행
# schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
