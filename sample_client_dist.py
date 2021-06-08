import urllib.request as r
import urllib.parse as p
import json
import pandas as pd
import ssl
import re
import konlpy
from konlpy.tag import Kkma
import string
from app.module import dbModule
import math

# todo TABLE body, 월, merge request

def do_content_date(int_year):
    round = int_year % 10
    decade = int_year - round
    chkrContent = db_class.executeOne("SELECT RID FROM testDB.content_date WHERE RID = '%d' AND decade = '%d'" % (rid, decade))
    if chkrContent is None:
        db_class.execute("INSERT INTO testDB.content_date(RID, decade) VALUES('%d', '%d')" % (rid, decade))


db_class = dbModule.Database()
kkma=Kkma()
for page in range(1, 49):
    url = "https://kubic.handong.edu:15000/retrieve_all?"
    serviceKey = "QyEqZtZ1vC-MNfq_NgsBEQ"
    numOfCnt = 200

    option = "serviceKey="+serviceKey
    request = ""
    request = "&numOfCnt="+p.quote(str(numOfCnt))+"&page="+p.quote(str(page))
    url_full = url + option + request

    print()
    print("url>"+url_full)

    context = ssl._create_unverified_context()
    response = r.urlopen(url_full, context=context).read().decode('utf-8')
    jsonArray = json.loads(response)

    if jsonArray.get("header").get("resultCode") != 200:
        print("Error!!!")
        print(jsonArray.get("header"))
        quit()

    items =jsonArray.get("body").get("contents")

    df = pd.DataFrame(columns=['title', 'body', 'writer', 'date', 'institution', 'institutionURL', 'fileURL', 'fileName', 'fileContent'])

    for item in items:
        df = df.append(item, ignore_index=True)

    db_class = dbModule.Database()

    for i, item in df.iterrows():
        if item.title is not None:
            item.title = item.title.strip()
            item.title = item.title.replace("\'","\\\'")
            item.title = item.title.replace("%","%%")

        if item.fileURL is not None:
            item.fileURL = item.fileURL.strip()
            item.fileURL = item.fileURL.replace("\'","\\\'")
            item.fileURL = item.fileURL.replace("%","%%")

        if item.writer is not None:
            item.writer = item.writer.strip()
            item.writer = item.writer.replace("\'","\\\'")
            item.writer = item.writer.replace("%","%%")

        print()
        print("page:", page, "iterator:", i)
        print("title", item.title)

        # institution
        sql1= "INSERT INTO testDB" \
              ".institution(institution_name,institution_url) VALUES('%s','%s') ON DUPLICATE KEY UPDATE institution_name='%s'"%(item.institution, item.fileURL, item.institution)
        db_class.execute(sql1)

        # writer
        sql2= "INSERT INTO testDB" \
              ".writer VALUES (NULL,'%s') on duplicate key update writer_name=writer_name"%(item.writer)
        db_class.execute(sql2)

        # research
        sql3= "INSERT INTO testDB" \
              ".research(title,research_url,institution_name,tot_word_cnt) VALUES('%s','%s','%s','%s')"%(item.title, item.fileURL, item.institution, 0)

        db_class.execute(sql3)

        rid = db_class.cursor.lastrowid
        db_class.commit()

        wid = db_class.executeOne("select WID from testDB"
                                  ".writer where writer_name='%s'"%item.writer)
        db_class.commit()

        sql2_1= "update testDB" \
                ".research set WID=('%s') where testDB" \
                ".research.RID='%d'"%(wid['WID'], rid)
        db_class.execute(sql2_1)
        db_class.commit()
        # keyword
        word_cnt = 0
        if item.body is not None:
            print(rid, " -- ", item.body)
            words = str(item.body)

            words = re.sub(r'[^ ㄱ-ㅣ가-힣 -~]', ' ', words)
            toInsert = words.replace("\'","\\\'")
            toInsert = toInsert.replace("\"","\\\"")
            toInsert = toInsert.replace('%', '%%')
            db_class.execute('INSERT INTO testDB.body(RID, body) VALUES("%d", "%s")' % (rid, toInsert))

            words = re.sub(r'[^ ㄱ-ㅣ가-힣0-9A-Za-z]', ' ', words)
            print(rid, " +- ", words)
            words = words.strip()
            if words == '':
                continue
            words = kkma.pos(words, flatten=False)
            for keyword in words:
                for index in range(len(keyword)):
                    if keyword[index][1] == "NNG":
                        sqlKey = "INSERT INTO testDB.keyword(word, RID, freq) VALUES('%s','%d','%d') ON DUPLICATE KEY\
                            UPDATE freq=freq+1" % (keyword[index][0], rid, 1)

                    elif keyword[index][1] == 'NNM' and keyword[index][0] == '년':
                        year = keyword[index-1][0]
                        try:
                            intYear = int(year)
                        except ValueError:
                            print("failed convert year to int")
                            continue
                        print(">>", intYear)
                        digits = int(math.log10(intYear)) + 1

                        #content_date

                        if digits == 4:
                            do_content_date(intYear)
                            sqlKey = "INSERT INTO testDB.keyword(word, RID, freq) VALUES('%s','%d','%d') ON DUPLICATE KEY\
                                                        UPDATE freq=freq+1" % (year, rid, 1)
                        else:
                            continue

                    elif keyword[index][1] == 'NNM' and keyword[index][1] == '월':
                        monthNum = keyword[index - 1][0] + '월'
                        print("---", monthNum, type(monthNum))
                        sqlKey = "INSERT INTO testDB.keyword(word, RID, freq) VALUES('%s','%d','%d') ON DUPLICATE KEY\
                         UPDATE freq=freq+1" % (monthNum, rid, 1)

                    else:
                        continue
                    word_cnt = word_cnt + 1
                    db_class.execute(sqlKey)
                    db_class.commit()
        print("body word count: ", word_cnt)
        db_class.execute("UPDATE testDB.research SET tot_word_cnt = '%s' WHERE RID = '%d'"%(word_cnt, rid))
        db_class.commit()

        # pub_date
        if item.date is not None:
            item.date = item.date.replace("\n","")
            item.date = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', item.date)

            if len(item.date)>=8:
                year = int(item.date[0:4])
                month = int(item.date[4:6])
                date = int(item.date[6:8])
                sql4= "INSERT INTO testDB" \
                  ".pub_date(RID,year,month,date) VALUES('%s','%s','%s','%s')"%(rid,year, month, date)

            elif len(item.date)>=6:
                year = int(item.date[0:4])
                month = int(item.date[4:6])
                sql4= "INSERT INTO testDB" \
                      ".pub_date(RID,year,month) VALUES('%s','%s','%s')"%(rid,year, month)

            elif len(item.date)>=4:
                year = int(item.date[0:4])
                sql4= "INSERT INTO testDB" \
                      ".pub_date(RID,year) VALUES('%s','%s')"%(rid,year)

            else:
                sql4= "INSERT INTO testDB" \
                      ".pub_date(RID,year) VALUES('%s','%s')"%(rid,item.date)
            db_class.execute(sql4)

            db_class.commit()

    #print(item)


