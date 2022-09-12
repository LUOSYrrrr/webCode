import pandas as pd
from pymongo import ReplaceOne


class Process:
    def __init__(self, config, mongo):
        self.config = config
        self.mongo = mongo

    # app.route相关
    def getgroup(self):
        groups = self.mongo.select_all(collection='group2id')
        return groups

    def getusers(self, table):
        return self.mongo.select_all(collection=table)

    def rankbyf(self, table):
        collection = self.mongo.db[table]
        return collection.find(filter={}, projection={'id': 1, 'frequency': 1}). sort([('frequency',-1)]).limit(10)

    def getuser(self, id):
        # print('the type of id from url:'+str(type(id)))!!!!前端传来的为字符串格式
        user=self.mongo.select_one(collection=self.config.group['table'],query={'id': int(id)})
        # print('you are in get user from :'+self.config.group['table'])
        return user

    # getuserinfo相关
    def get_bing(self, l1, l2):
        return set(l1) | set(l2)

    def clearpunc(self, s1):
        punc = '，。、【】“”：；（）《》‘’{}？！⑦()%^<>℃^￥‎ '
        s2 = ''
        for ch in s1:
            if ch not in punc:
                s2 += ch
        return s2

    def justify_latest(self, t1, t2):
        if (t1 > t2):
            return t1
        else:
            return t2

    # 合并两条userinfo，集合
    def update_single(self, old, new):
        res = {}
        res['id'] = old['id']
        res['latest'] = self.justify_latest(old['latest'], new['latest'])
        res['frequency'] = old['frequency'] + 1
        res['kmeans'] = old['kmeans']
        for key in old.keys():
            if (key not in ['id', 'latest', 'frequency', 'kmeans']):
                res[key] = self.get_bing(old[key], new[key])
        return res

    # mongodb无法解析set集合
    def set2list(self, single):
        res = {}
        for key in single.keys():
            if (key in ['id', 'latest', 'frequency', 'kmeans']):
                res[key] = single[key]
            else:
                res[key] = list(single[key])
        return res

    def updatett(self, collection, data, new=False):
        print('update database...')
        allid = self.mongo.getallid(collection=collection)
        idata, udata = [], []  # insert, update
        for item in data.items():
            item = item[1]
            if (allid and (item['id'] in allid)):  # 更新
                old_single = self.mongo.select_one(collection=collection, query={'id': item['id']},projection={'_id': 0})
                new_single = self.update_single(old_single, item)
                udata.append(self.set2list(new_single))
            else:  # 插入新数据
                idata.append(self.set2list(item))
        print('*******正在插入新用户，共计' + str(len(idata)) + '*************')
        if idata:
            ret = self.mongo.db[collection].insert_many(idata)
            print(ret)
        # pymongo批量操作
        bulk = self.mongo.db[collection]
        bulkArr = []
        print('*******正在更新老用户信息，共计' + str(len(udata)) + '*************')
        if udata:
            for item in udata:
                bulkArr.append(
                    ReplaceOne(filter={'id': item['id']}, replacement=item)
                )
            ret = bulk.bulk_write(bulkArr)
            print(ret)
        return len(idata),len(udata)


    # kmeans相关
    # dataframe无法解析list
    def list2str(self,row):
        for key,item in row.items():
            if key in self.config.l_header:
                row.update({key:' '.join(item)})
        return row

    # 注意不需要kmeans字段和latest字段？
    def table2df(self):
        alldata=self.mongo.select_all(collection=self.config.group['table'],projection={'_id':0,'kmeans':0})
        print('***************get DataFrame****************')
        dftemp=[]
        for row in alldata:
            dftemp.append(self.list2str(row))
        self.df=pd.DataFrame(dftemp,columns=self.config.header)
        self.df.fillna(value=0, inplace=True)

    # 是否需要对id进行线性归一化。。？
    def normalization(self):
        print('****************归一化******************')
        columns = ['frequency']
        for column in columns:
            if self.df[column].max() != self.df[column].min():
                self.df[column] = (self.df[column] - self.df[column].min()) / (
                            self.df[column].max() - self.df[column].min())

    def onehot(self):
        print('*********onehot encode*************')
        columns=['latest','topic', 'per', 'loc', 'org', 'time', 'contact']
        for column in columns:
            df_dummies2 = pd.get_dummies(self.df[column], prefix=column)
            self.df = self.df.drop(column, axis=1)
            self.df = pd.concat([self.df, df_dummies2], axis=1)

    def formal_data(self):
        self.table2df()
        self.normalization()
        self.onehot()
        # print(self.df.head(1))
        return self.df

