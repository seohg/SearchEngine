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

def findDocumentsForQuery(query):
    query = re.sub(r'[^ ㄱ-ㅣ가-힣A-Za-z//s]', '',query)
    query = kkma.pos(query,flatten=False)


    
    BM25ScoreList = {}

    for term in query:
        # docDit={} rid 저장
        # N = 문서의 수
        # select_q = select count(*) from 
        # dft = 단어를 포함하고 있는 문서의 수
        # ftd = 문서에 포함되는 단어의 빈도
        # k = TF의 saturation을 결정하는 요소 (1.2~2.0의 값을 사용하는 것이 일반적)
        # b = 일반적으로 0.75 사용, b가 0에 가까워지면 문서의 길이에 대한 부분은 무시됨
        # ld = tot_word_cnt
        # avgld = tot_word_cnt 평균
        for doc in docDict:
            BM25 = calculateBM25(N, dft, ftd, k, b,ld, avgld)
            BM25ScoreList[doc] += BM25
    return BM25ScoreList


'''
def writeToFile(queries, invertedIndex, fileLengths):

    queryID = 1
    file = open(BM25_SCORE_STOPPED_LIST, "w")       
    queryNames = open(QUERY, 'r').read().splitlines()
    for query in queries:
        BM25ScoreList = findDocumentsForQuery(query, invertedIndex, fileLengths, queryID)
        sortedScoreList = sorted(BM25ScoreList.items(), key=lambda x:x[1], reverse=True)
        for rank in range(100):
            text = str(queryID) +  "   " + "Q0" +  "   " + str(sortedScoreList[rank][0]) + "   " + str(rank+1) +  "   " + str(sortedScoreList[rank][1]) +  "   " + "BM25" + "\n"
            file.write(text)
        file.write("\n\n ---------------------------------------------------------------------------------------\n\n\n")
        queryID += 1
    file.close()
'''

def BM25(N, dft, ftd, k, b,ld, avgld):
    '''
    N = 문서의 수
    dft = 단어를 포함하고 있는 문서의 수
    ftd = 문서에 포함되는 단어의 빈도
    k = TF의 saturation을 결정하는 요소 (1.2~2.0의 값을 사용하는 것이 일반적)
    b = 일반적으로 0.75 사용, b가 0에 가까워지면 문서의 길이에 대한 부분은 무시됨
    ld = tot_word_cnt
    avgld = tot_word_cnt 평균
    '''
   
    Q1 = log(1+(N - dft + 0.5)/(dft+0.5))
    Q2 = ftd/(ftd+k*(1-b+b*(ld/avgld)))

    return Q1 * Q2 
