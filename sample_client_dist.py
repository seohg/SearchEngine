import urllib.request as r
import urllib.parse as p
import json
import pandas as pd
import ssl

from app.module import dbModule

url = "https://kubic.handong.edu:15000/retrieve_all?"
serviceKey = "QyEqZtZ1vC-MNfq_NgsBEQ"
numOfCnt = 200
page =2

option = "serviceKey="+serviceKey
request = ""
request = "&numOfCnt="+p.quote(str(numOfCnt))+"&page="+p.quote(str(page))
url_full = url + option + request


print("url>"+url_full+"numOfCnt="+"10")
context = ssl._create_unverified_context()
response = r.urlopen(url_full,context=context).read().decode('utf-8')
#print(response)

jsonArray = json.loads(response)

if jsonArray.get("header").get("resultCode") != 200:
    #print("Error!!!")
    print(jsonArray.get("header"))
    quit()

items =jsonArray.get("body").get("contents")
#print("items>", items)

df = pd.DataFrame(columns=['title', 'body', 'writer', 'date', 'category', 'institution', 'file'])
for item in items:
    df = df.append(item, ignore_index=True)
  #  print(df)


'''
 아래 코드는 임의로 간단한 테이블 만들어서 db에 데이터가 들어가는지 확인하려고 간단하게 틀만 만들어둔 부분입니다.
 데이터베이스를 설계해서 만든 후에 page로 for문 돌리고 sql 수정한 후에 넣으면 될 것 같아요!
 dbModule.py에서 DB 정보 수정한 후에 사용하세요
 그리고 테이블 만들때 한글 설정 안하면 오류나요~ 꼭 설정해주세용ㅎㅎ
'''

db_class = dbModule.Database()
for i, item in df.iterrows():

    #print(item.title)
    sql= "INSERT INTO testDB.title(title) VALUES('%s')"%item.title
    # testDB = db이름 , title=table이름 ,(title) = attribute이름
    
    db_class.execute(sql)
    #print(item)

    #break
    
db_class.commit()
