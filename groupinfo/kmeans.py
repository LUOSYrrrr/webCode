import time

import pandas as pd
from utils.process import Process
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans  # 导入K均值聚类算法
from sklearn.decomposition import PCA  # 进行降维处理
import numpy as np
from pymongo import UpdateOne
from sklearn import metrics


class KmeansModel():
    # 包括读取数据，数据格式化和onehot编码
    def __init__(self,config,mongo,group):
        self.config=config
        self.mongo=mongo
        self.process = Process(config,mongo)
        self.df=self.process.formal_data()
        self.group=group
        self.collection=group['table']

    def draw(self,k, data, centers):
        fig, axes = plt.subplots(1, 1)
        # 解决显示中文乱码
        pca = PCA(n_components=2)
        new_data = pca.fit_transform(data)
        axes.scatter(new_data[:, 0], new_data[:, 1], c='b', marker='o', alpha=0.5)
        axes.scatter(centers[:, 0], centers[:, 1], c='r', marker='*', alpha=0.5)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        plt.title("群成员分类 k="+str(k))
        sd_path='static/images/kmeans_'+self.group['table']+'.png'
        plt.savefig(sd_path, dpi=150)
        plt.close()

    def kmeans_model(self,k=5,train=False):
        self.data = np.array(self.df.iloc[:, 1:])
        kmeans = KMeans(n_clusters=k).fit(self.data)
        centers = kmeans.cluster_centers_  # 获取中心点
        pca = PCA(n_components=2)  # 设置维度
        self.centers_d = pca.fit_transform(centers)
        self.labels = kmeans.labels_  # 获取聚类标签
        if train:
            inertia = kmeans.inertia_
            return inertia
        else:
            if(len(np.unique(self.labels))==0):
                print('只有一个labels')
                return -1
            else:
                # print(np.unique(self.labels))
                silhouette = metrics.silhouette_score(self.data, self.labels, metric='euclidean')  # 得到每个k下的平均轮廓系数
                return silhouette

    def updatek(self,best_labels):
        ids=list(self.df['id'])
        labels=best_labels.tolist() #labels是numpy格式，mongodb不允许
        bulk = self.mongo.db[self.collection]
        bulkArr = []
        if(len(ids)!=len(labels)):
            print('error in label2id!!!!!!!!')
            exit(1)
        for i in range(len(labels)):
            bulkArr.append(
                UpdateOne({'id':ids[i]},{'$set':{'kmeans':labels[i]}},upsert=True)
            )
        ret=bulk.bulk_write(bulkArr)
        print(ret)

    def run_kmeans(self):
        start=time.time()
        print('开始更新群用户聚类情况：'+str(start))
        labels=self.kmeans_k()
        print('模型建立完毕，已获取聚类结果。'+str(time.time()-start))
        self.updatek(labels)
        print('kmeans字段更新完毕。' + str(time.time() - start))


    def kmeans_k(self):
        # 轮廓系数法
        score_list = []
        best_labels, best_centers_d = None, None  # 初始化
        silhouette_int = -1  # 初始化的平均轮廓阀值
        best_k = 2  # 初始化k值
        for n_clusters in range(2, 11):  # 遍历从2-10几个有限组
            if n_clusters >= self.df.shape[0]:
                break
            silhouette_tmp = self.kmeans_model(n_clusters, train=False)
            if silhouette_tmp > silhouette_int:  # 如果平均轮廓系数更高
                best_k = n_clusters  # 将最好的k存储下来
                silhouette_int = silhouette_tmp  # 将最好的平均轮廓得分存储下来
                best_labels = self.labels  # 将最好的聚类标签存储下来
                best_centers_d = self.centers_d
            score_list.append([n_clusters, silhouette_tmp])

        print('{:-^60}'.format('K value and silhouette summary:'))
        print(np.array(score_list))  # 打印输出k下的详细得分
        print('Best K is:{0} with average silhouette of {1}'.format(best_k, silhouette_int.round(4)))
        self.draw(best_k, self.data, best_centers_d)
        return best_labels
        # 遍历，根据inertia值找到拐点，寻找最佳k值,手肘法
        # list = []
        # for k in range(2, 25):
        #     print('当前聚类数目为：', k)
        #     list.append([k, self.kmeans_model(k,train=True)])
        # print(list)
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 1, 1)
        # array = np.array(list)
        # ax.plot(array[:, 0], array[:, 1],marker='.')
        # plt.savefig('data/k.png',dpi=150)
        # plt.show()

