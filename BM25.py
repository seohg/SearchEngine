import os
from math import log

import urllib.request as r
import urllib.parse as p
import json
import pandas as pd
import ssl
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import konlpy
from konlpy.tag import Kkma

import string
from app.module import dbModule

db_class = dbModule.Database()
kkma=Kkma()

def findDocumentsForQuery(title):
    #parsing
    title = dict(title)
    searchkey = title['key']

    searchkey = re.sub(r'[^ ㄱ-ㅣ가-힣A-Za-z//s]', '',searchkey)
    searchkey = kkma.pos(searchkey,flatten=False)

    BM25ScoreList = {}


    for term in searchkey:
        docDict=[]
        print(term[0][0])
        print("111")
        RID = db_class.executeAll("select RID, freq from testDB.keyword where word='%s'"%term[0][0])
        for row in RID:
            docDict.append([row['RID'], row['freq']])
        print("22")
        print(docDict)

        for doc in docDict:
            n = 9600
            dft = len(docDict)
            ftd = doc[1]
            # k = TF의 saturation을 결정하는 요소 (1.2~2.0의 값을 사용하는 것이 일반적)
            k=1.5
            # b = 일반적으로 0.75 사용, b가 0에 가까워지면 문서의 길이에 대한 부분은 무시됨
            b=0.75
            ld = db_class.executeOne("SELECT tot_word_cnt FROM testDB.research WHERE RID = '%d'" % doc[0])
            ld = ld['tot_word_cnt']

            avgld = db_class.executeOne("SELECT AVG(tot_word_cnt) FROM testDB.research WHERE RID IN(SELECT RID FROM testDB.keyword WHERE word ='%s')" %
            term[0][0])
            avgld = float(avgld['AVG(tot_word_cnt)'])

            BM25 = cBM25(n, dft, ftd, k, b,ld, avgld)
            tRid = str(doc[0])
            if tRid in BM25ScoreList.keys():
                tmp = BM25ScoreList[tRid]
                tmp = tmp + BM25
                BM25ScoreList[tRid] = tmp
            else:
                BM25ScoreList[tRid] = BM25


    sortedScoreList = sorted(BM25ScoreList.items(), key=lambda x: x[1], reverse=True)
    sortedList = list(sortedScoreList)
    Result = []
    i =0
    for item in sortedList:
        tResult=[]
        if i == 5:
            break;
        i = i+1
        #query
        tResult.append(item[0])
        first = db_class.executeOne(
            "SELECT title, institution_name, WID FROM research WHERE RID = '%d'" % int(item[0]))

        tResult.append(first['title'])
        tResult.append(first['institution_name'])

        second = db_class.executeOne("SELECT year, month, date FROM pub_date WHERE RID = '%d'" % int(item[0]))

        date =""
        if second is not None:
            if second['year'] is not None:
                date = str(second['year'])
                if second['month'] is not None:
                    date = str(second['year']) + str(second['month'])
                    if second['date'] is not None:
                        date = str(second['year']) + str(second['month']) + str(second['date'])

        tResult.append(date)

        third = db_class.executeOne("SELECT writer_name FROM writer WHERE WID = '%d'" % int(first['WID']))
        tResult.append(third['writer_name'])

        #tResult.append()
        Result.append(tResult)

    print(Result)
    return Result


def cBM25(N,dft,ftd,k, b,ld,avgld):
    Q1 = log(1+(N - dft + 0.5)/(dft+0.5))
    Q2 = ftd/(ftd+k*(1-b+b*(ld/avgld)))
    return Q1 * Q2
