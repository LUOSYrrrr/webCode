"""
将一个群的多条群聊消息整合成一个语料块
"""
import pymongo
import jieba.analyse
import re
import string
from zhon.hanzi import punctuation

class wordProcess():
    def __init__(self,group):
        self.punctuation_string = string.punctuation  # 用于预处理标点

        self.client = pymongo.MongoClient('localhost', 27017)  # 建立连接，一般默认
        self.db = self.client['localhost']  # 引号内为数据库的名字（原始群聊消息）  ---1
        self.group = group
        self.chat_name = group['rtable']  # 逐条消息存储的数据库表名  ---2
        self.chat_collection = self.db[self.chat_name]
        self.row_collection_name = 'row_chat'  # 存储分词后的消息  ---3
        self.row_collection = self.db[self.row_collection_name]


    def one_processing(self,line):
        jieba.analyse.set_stop_words(
            "data/all_stopwords.txt"  # 引用停词表  ---4
        )
        jieba.load_userdict("data/need_words.txt")  # ---5

        msg = ''
        tags = jieba.analyse.extract_tags(line, topK=10)  # 利用jieba库基于tf-idf提取每句关键信息，设定最多topK个词，列表类型
        print(tags)

        # 从tags列表中提取每个关键词写入新的数据库表
        number = len(tags)
        if number != 0:  # 没有关键词则跳过
            str = ''
            for i in range(0, number):
                word1 = re.sub(r"[A-Za-z]", '', tags[i])
                word2 = re.sub(r"[0-9]+", '', word1)
                word3 = re.sub('[{}]'.format(self.punctuation_string), '', word2)
                word4 = re.sub('[{}]'.format(punctuation), '', word3)
                if len(word4) == 0:
                    continue
                else:
                    str = str + word4 + ' '

            if len(str) != 0:
                print('one_msg_words: ' + str)
                msg = msg + str

        return msg


    def msg_processing(self):
        self.row_collection.drop()
        row_msg = ''
        cut_msg = ''
        for one in self.chat_collection.find():
            one_msg = one["message"]
            row_msg = row_msg + one_msg + ' '

            cut_word = self.one_processing(one_msg)
            if len(cut_word) != 0:
                cut_msg += cut_word
        print(row_msg)
        print('**###################')
        print(cut_msg)

        data = {"chat_name": self.chat_name, "row_msg": row_msg, "cut_msg": cut_msg}
        self.row_collection.insert_one(data)



