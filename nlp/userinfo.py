from nlp.ner import Ner
from nlp.cnn import TextCNN
import time as jishi
import matplotlib.pylab as plt
from utils.process import Process


class UserInfo():
    def __init__(self, config, mongo,group):
        self.config = config
        self.process = Process(config, mongo)
        self.mongo = mongo
        self.cnn = TextCNN(config)
        self.ner = Ner()
        self.repeat = 0
        self.nums=[0,0,0,0,0,0]
        self.group=group

    def getplot(self, data):
        # print(data)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.bar(range(len(data)), data, tick_label=self.config.categories)
        plt.xticks(rotation=30)
        plt.title('TextCNN result')
        cnn_path='static/images/cnn_'+self.group['table']+'.png'
        plt.savefig(cnn_path, dpi=150)
        plt.close()

    def getinfo(self):
        start = jishi.time()
        print('开始进行NLP处理: ' + str(start))
        allrows = self.mongo.select_all(collection=self.group['rtable'])
        alltemp = {}
        # 处理每一条message得到alltemp dict
        for line in allrows:
            text = line['message']
            if(text=='None'):   # 过滤None数据
                continue
            per, loc, org, time = self.ner.plot(text)
            contact = self.ner.contact(text)
            topic = self.cnn.predict(text)
            single = {'id': line['id'], 'latest': line['date'], 'topic': {topic}, 'per': per, 'loc': loc, 'org': org,
                      'time': time, 'contact': contact, 'frequency': 1, 'kmeans': 0}
            print(single)
            # 判断在此轮数据中是否有重复出现用户
            if str(line['id']) not in alltemp.keys():
                alltemp[str(line['id'])] = single
            else:
                temp = alltemp[str(line['id'])]
                alltemp.update({str(line['id']): self.process.update_single(temp, single)})
                self.repeat += 1
        print('共有' + str(self.repeat) + '次重复数据')
        self.getplot(self.cnn.nums)
        print('训练数据得到info共耗时：' + str(jishi.time() - start))
        # 将一个table中重复的数据合并
        len_insert,len_update=self.process.updatett(self.group['table'], alltemp)
        print('得到info并插入数据库共耗时：' + str(jishi.time() - start))
        return [self.repeat,len_insert,len_update,round(jishi.time() - start,3)]
