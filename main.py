# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import codecs
import webbrowser
from datetime import datetime

# 오늘의 연월일 찾기
today = datetime.now()
year = int(today.year)
month = int(today.month)
day = int(today.day)

# 파일명 지정 (오늘 날짜로)
filename = '%d-%02d-%02d.html' % (year, month, day)

# 크롬 드라이브 열기
driver = webdriver.Chrome()
# 브라우저 크기 최대화
driver.maximize_window()
# 목표 싸이트 주소로 이동
driver.get("http://www.named.com")


# 아이디 비번 저장한 파일 열기
secure = open('secure.txt', 'r')
secure_text = secure.readlines()
secure.close()

# 위의 파일에서 아이디 비번 읽어오기
ID = secure_text[0].split(':')[1].strip()
PW = secure_text[1].split(':')[1].strip()

# 네임드 싸이트 로그인하기
find_id = driver.find_element_by_id("mb_id")
find_id.send_keys(ID)
find_pw = driver.find_element_by_id("mb_password")
find_pw.send_keys(PW)
find_pw.submit()

# 시간 패턴 입력
time_pattern = re.compile('[0-9]{2}:[0-9]{2}')

# 결과물을 저장하기 위한 파일 열기
# open을 하지않고 codecs.open을 하는 이유는
# 기본적으로 ASCII로 파일을 저장하기 때문에 다른 인코딩으로
# 저장하기 위해서는 codecs 라이브러리를 사용해야한다. (내장 라이브러리)
w = codecs.open(filename,'w','utf-8')

# UTF-8 Meta -> 글자 깨짐 방지
w.write('<meta charset="utf-8">'.decode('utf-8'))
# 간단 스타일 주기
w.write("<style>h1 {font-family: 굴림;color: tomato;background-color:#333; border-bottom: 5px double #ccc; padding: 15px 0px; margin: 0px; text-align:center;} h2 {background-color:#555;padding: 7px;color: CadetBlue;margin:0px;text-align: right;}#artcBody{padding: 25px;border:1px dashed silver;}</style>".decode('utf-8'))

# 시작 페이지 초기값
page = 1

# 반복문을 통하여 1페이지부터 1씩 증가하여 2페이지, 3페이지 나아간다.
while True:
    URL = 'http://named.com/bbs/board.php?bo_table=odds&page=%d' % page
    driver.get(URL)
    html = driver.page_source

    # 이 페이지에서 오늘 것을 하나라도 찾았는지 유무를 위해 변수 지정
    today_exists = False

    soup = BeautifulSoup(html,"html.parser", from_encoding='utf-8')
    tr_list = soup.find_all('tr',{'class': ''})

    for tr in tr_list[2:]:
        td_list = tr.find_all('td')
        a = td_list[0].find_all('a')

        title = a[1].get_text()
        time = str(td_list[2].get_text())
        link = a[1]['href']

        if len(time_pattern.findall(time)) > 0:
            # 오늘 날짜것을 찾았다면 참을 저장함
            today_exists = True
            # 제목과 업로드 시간
            w.write('<h1>'+title+'</h1>')
            w.write('<h2>'+time+'</h2>')

            driver.get("http://www.named.com/" + link)

            soup = BeautifulSoup(driver.page_source, "html.parser", from_encoding='utf-8')
            a = str(soup.find_all('div', {"id":"artcBody"})[0])
            contents = a[:a.find('<div class="grade_area">')].decode('utf-8', 'ignore')

            # 내용 파일에 입력
            w.write(contents)

            # 뒤에 javascript 제거함으로써 뒤에 div닫아주는게 제거되서 다시 넣음
            # 게시물과의 차이를 두기 위해 선을 그음
            w.write('</div><hr />')
    if today_exists == False:
        # 오늘것을 하나도 못찾아서 참 저장이 안되었으므로 반복문 종료
        w.write('No data for today')
        break
    else:
        # 반복문 계속 진행하고 페이지수 + 1 해줌.
        page += 1
        continue

w.close()
driver.quit()

# webbrowser를 이용하여 저장한 html파일 브라우저로 열기
webbrowser.open(filename)
