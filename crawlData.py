#import io
#import sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
from pymongo import MongoClient
from pymongo import *
from telethon.sync import TelegramClient

import json
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import pymongo
import emoji
import json
import datetime
import asyncio
import socket
import socks
class crawlData():
    def __init__(self):
        #self.proxy = (socks.SOCKS5, '42.202.33.44', 12306, True, 'RC65BT6BWX', 'Et3DFEEfR3')
        self.MONGO_HOST="127.0.0.1"
        self.MONGO_PORT=27017
        self.MONGO_DB='localhost'
        self.myclient=pymongo.MongoClient(host=self.MONGO_HOST,port=self.MONGO_PORT)
        self.db=self.myclient[self.MONGO_DB]
        self.api_id = 9243639  # 输入api_id，一个账号一项
        self.api_hash = '725089e9c7292eaafad3cbfcde0d6ca4'
        self.phone = "+8613691350052"
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash,proxy=self.proxy,connection_retries=1)
        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            self.client.sign_in(self.phone, input('Enter the code: '))
        self.chats = []
        self.last_date = None
        self.chunk_size = 200
        self.groups = []
        self.result = self.client(GetDialogsRequest(
            offset_date=self.last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=self.chunk_size,
            hash=0
        ))
        self.datalist = []
        self.chats.extend(self.result.chats)
        for chat in self.chats:
            try:
                if chat.megagroup == True:
                    self.groups.append(chat)
            except:
                continue


    def getGroupName(self):
        self.datalist = []
        col = self.db['group']

        for x in col.find():
            self.datalist.append(x)
        print(self.datalist)
        return self.datalist



    def updateGroupName(self):
        collection2 = self.db['group2id']
        collection2.drop()
        i=1


        for g in self.groups:
            # print( str(g.id))
            nowtime = datetime.datetime.now()



            tableName = str(g.id)
            MONGO_COLL = tableName
            collection1 = self.db[str('r'+str(i))]

            groupmessage = {'id': str(i),'name': g.title,'table': str('t'+str(i)),'rtable': str('r'+str(i)),'update_time': nowtime,'groupId':str(g.id)}
            # print(groupmessage)
            collection2.insert_one(groupmessage)
            i=i+1
            j = 0

            for message in self.client.iter_messages(g):
                if (j > 2000): break
                if type(message.text) != 'str':
                    message.text = str(message.text)
                if (len(message.text) == 0): message.text = '无消息'
                result = emoji.demojize(message.text)

                messagetime = datetime.datetime(message.date.year, message.date.month, message.date.day)

                nowtime = datetime.datetime.now()
                nowtime = datetime.datetime(nowtime.year, nowtime.month, nowtime.day)

                datediffer = (nowtime.__sub__(messagetime))
                print(datediffer)

                print("{'id':", message.sender_id, ",'date':'", message.date, ",'message':'", message.text, "'}")
                d = {"id": message.sender_id, 'date': message.date, "message": message.text}
                id = collection1.insert_one(d)
                j = j+1

        self.datalist = []
        col = self.db['group2id']

        for x in col.find():  # 查询集合中所有文档数据并且遍历
            self.datalist.append(x)
        print(self.datalist)
        return self.datalist

    def updateGroup(self):
        collection2 = self.db['group']
        collection2.drop()
        i=0
        for g in self.groups:
            tableName=str(g.id)
            print(type(g))
            MONGO_COLL=tableName
            collection1 = self.db[MONGO_COLL]

            collectionName=self.db['group2id'].find({groupId:g.title}, {rtable: 1})
            collection1 = self.db[collectionName]
            collection1.drop()
            nowtime = datetime.datetime.now()
            nowtime = datetime.datetime(nowtime.year, nowtime.month, nowtime.day)

            tableName = str(g.id)
            MONGO_COLL = tableName

            groupmessage = {'id': str(i), 'name': g.title, 'table': str('t' + str(i)), 'rtable': str('r' + str(i)),
                            'update_time': nowtime, 'groupId': str(g.id)}
            # print(groupmessage)
            collection2.insert_one(groupmessage)
            i = i + 1




        #for g in groups:

            #print(str(i) + '- ' + g.title)
            #i += 1

        #g_index = input("Enter a Number: ")
        #target_group = groups[int(g_index)]
        #print(target_group)
    #def getDetail(self,id):
        # for g in groups:
        #     print(g)
        #     print(g.id)
        #     print(client.iter_messages(g))
        #     tableName=str(g.id)
        #     print(type(g))
        #     MONGO_COLL=tableName
        #     collection1 = db[MONGO_COLL]
        #     collection2 = db['group']
        #     collection1.drop()
        #     groupmessage = {"groupId": str(g.id), 'groupName': g.title}
        #     print(groupmessage)
        #     collection2.insert_one(groupmessage)
        #
        #     i=0
        #     data_list = []
        #     for message in client.iter_messages(g):
        #         if (i > 1): break
        #         if type(message.text) != 'str':
        #             message.text = str(message.text)
        #         if (len(message.text) == 0): message.text = '无消息'
        #         result = emoji.demojize(message.text)
        #
        #         messagetime = datetime.datetime(message.date.year, message.date.month, message.date.day)
        #
        #         nowtime = datetime.datetime.now()
        #         nowtime = datetime.datetime(nowtime.year, nowtime.month, nowtime.day)
        #
        #         datediffer = (nowtime.__sub__(messagetime))
        #         print(datediffer)
        #
        #         print("{'id':", message.sender_id, ",'date':'", message.date, ",'message':'", message.text, "'}")
        #         d = {"id": message.sender_id, 'date': message.date, "message": message.text}
        #         id = collection1.insert_one(d)
        #         i = datediffer.days





