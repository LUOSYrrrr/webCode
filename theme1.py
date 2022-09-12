"""
将mongo中处理后的数据（已分词）进行初步主题挖掘

主题数暂定为5
根据困惑度分析和可视化结果分析，在”theme2.py“中进行主题数的调整，得到最终结果
"""
import string
import joblib
import pymongo
from sklearn.decomposition import LatentDirichletAllocation
from \
        sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pyLDAvis.sklearn

import matplotlib.pyplot as plt
class theme1():
    def __init__(self, group):
        self.punctuation_string = string.punctuation  # 用于预处理标点
        self.group = group
        self.chat_name = group['rtable']  # 逐条消息存储的数据库表名  ---2

        self.mainpath = 'static/themeResult'  # 其他处理结果所在文件夹 ---1

        # 数据库准备
        self.client = pymongo.MongoClient('localhost', 27017)  # 建立连接，一般默认
        self.db = self.client['localhost']  # 引号内为数据库的名字（原始群聊消息）  ---2
        self.topic_collection = self.db['topics']  # 将多个群聊对话进行主题挖掘后存放的表  ---3
        self.chat_collection = self.db['row_chat']  # 需要进行主题挖掘的数据(已分词)所在表  ---4
        self.n_topics = 5


    #################
    # 从mongo数据库中获取数据，得到含每个群聊消息的列表
    # create_word_list1():分析指定群
    # create_word_list1():分析所有群
    def create_word_list1(self):
        chat_list = []
        print(self.chat_name)
        name_list = [self.chat_name]   # 需要进行主题挖掘的群 ---5

        names = ''
        for name in name_list:
            names += name
            print(names)
            myquery = {"chat_name":name}
            msg = self.chat_collection.find({"chat_name":self.chat_name})

            for i in msg:
                chat_list.append(i["cut_msg"])
        print(len(chat_list))

        return chat_list, names


    def create_word_list2(self):
        word_group = self.chat_collection.distinct("words")  # 列名  ---6
        print(type(word_group))
        print(len(word_group))

        name_group = self.chat_collection.distinct("name")  # 列名  ---7
        names = ''
        for name in name_group:
            names += name

        return word_group, names


    # lda_word_list, chat_names = create_word_list2()
    #lda_word_list, chat_names = create_word_list1()

    ##############
    # 将文本数据转化为特征向量
    from \
        sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    #from sklearn.decomposition import LatentDirichletAllocation


    def verctotizer_train(self,lda_word_list):
        tf_vectorizer_train = CountVectorizer(strip_accents='unicode',
                                              max_features=1000,
                                              max_df=2,
                                              min_df=0.9)

        tf_train = tf_vectorizer_train.fit_transform(lda_word_list)  # 拟合模型，并返回文本矩阵
        model_path1 = self.mainpath + '/' + 'lda1.pkl'
        joblib.dump(tf_vectorizer_train, model_path1)  # 保存模型
        return tf_train, tf_vectorizer_train





    ####################
    # 查看该方法生成的停用词
    def stop_word(self,tf_vectorizer):
        stop_wordlist = list(tf_vectorizer.stop_words_)  # 把集合类型转化成列表类型，并写入itsstopwords.txt
        index = len(stop_wordlist)
        stop_wordpath = self.mainpath + '/' + 'itsstopwords.txt'  # 该方法生成的停用词的文件路径
        with open(stop_wordpath, 'w', encoding='utf-8') as f:
            for i in range(0, index):
                f.write(stop_wordlist[i] + '   ')


    #stop_word()

    ########################
    # LDA主题模型
    # 训练模型↓
    # --------------
    #n_topics = 5  # 主题数量，自定义，可以根据困惑度和可视化结果进行调整
    #ldamodel = LatentDirichletAllocation(n_components=n_topics, max_iter=50,  # 迭代数量：50
                                         #learning_method='batch',
                                         #                                 doc_topic_prior=0.1,  # α，不定义时默认位1/主题数
                                         #                                 topic_word_prior=0.01,  # β，不定义时默认位1/主题数
                                        # random_state=0)


    # 通过fit_transform函数，我们就可以得到文档的主题模型分布在ldaresult中
    # 而主题词分布则在ldamodel.components_中
    # ldaresult = ldamodel.fit_transform(tf)
    def lda_train(self,ldamodel,tf):
        result = ldamodel.fit_transform(tf)
        model_path2 = self.mainpath + '/' + 'lda' + '2.pkl'
        joblib.dump(result, model_path2)
        return result


    #ldaresult = lda_train()

    # --------------------

    # print('**ldaresult**:')
    # print(ldaresult)
    # print('**ldamodel**:')
    # print(ldamodel.components_)
    # print('**perplexity**')
    # print(ldamodel.perplexity(tf))  # 收敛效果,perplexity:主题困惑度

    ##############
    # LDA可视化、困惑度分析

    # import pyLDAvis.sklearn
    # import pyLDAvis.sklearn

    # pic = pyLDAvis.sklearn.prepare(ldamodel, tf, tf_vectorizer, mds='mmds')
    # pyLDAvis.display(pic)
    # picpath = mainpath + '/' + 'lda_pass_before.html'
    # pyLDAvis.save_html(pic, picpath)

    #############
    # 利用困惑度找到最佳主题数量
    import matplotlib.pyplot as plt


    def perplexity_analyze(self,tf):
        plexs = []
        perplexity = ''
        n_max_topics = 16
        for i in range(1, n_max_topics):
            lda = LatentDirichletAllocation(n_components=i, max_iter=50,
                                            learning_method='batch',
                                            learning_offset=50, random_state=0)
            lda.fit(tf)
            plexs.append(lda.perplexity(tf))
            perplexity = perplexity + str(i) + ':' + str(lda.perplexity(tf)) + '\n'
            print(i)
            print(lda.perplexity(tf))

        n_t = 15  # 区间最右侧的值。注意：不能大于n_max_topics
        x = list(range(1, n_t))
        plt.plot(x, plexs[1:n_t])
        plt.xlabel("number of topics")
        plt.ylabel("perplexity")
        plt.savefig(self.mainpath + '/' + 'plt.png')

        return perplexity


    #perplexity_result = perplexity_analyze()

    ########################
    # 打印对应主题下的前n_top_words个关键词，并写入文档topic-words.txt
    #topicpath = mainpath + '/' + 'topic_words_before.txt'


    def print_top_words(self,model, feature_names, n_words,topicpath,chat_names,perplexity_result):
        # 打印每个主题下权重较高的词
        words = ''
        ff = open(topicpath, 'w', encoding='utf-8')
        ff.write(chat_names)
        ff.write("\n")
        for topic_idx, topic in enumerate(model.components_):
            print("Topic #%d:" % topic_idx)
            words = words + str(topic_idx) + '、'
            for n in topic.argsort()[:-n_words - 1:-1]:
                print(feature_names[n], end=' ')
                words = words + feature_names[n] + ' '
                ff.write(feature_names[n] + '   ')
            print()
            words = words + '\n'
            ff.write('\n')

        data = {'name': chat_names, 'topic_words': words, 'perplexity': perplexity_result}
        self.topic_collection.delete_many({'name': chat_names})

        self.topic_collection.insert_one(data)
        ff.close()


    # n_top_words = 20  # 打印的主题词数  ---7
    # tf_feature_names = tf_vectorizer.get_feature_names_out()
    # print_top_words(ldamodel, tf_feature_names, n_top_words)

    def runTheme(self):
        lda_word_list, chat_names = self.create_word_list1()
        tf, tf_vectorizer = self.verctotizer_train(lda_word_list)
        self.stop_word(tf_vectorizer)
        ldamodel = LatentDirichletAllocation(n_components=self.n_topics, max_iter=50,  # 迭代数量：50
                                             learning_method='batch',
                                             #                                 doc_topic_prior=0.1,  # α，不定义时默认位1/主题数
                                             #                                 topic_word_prior=0.01,  # β，不定义时默认位1/主题数
                                             random_state=0)
        ldaresult = self.lda_train(ldamodel,tf)
        print('**ldaresult**:')
        print(ldaresult)
        print('**ldamodel**:')
        print(ldamodel.components_)
        print('**perplexity**')
        print(ldamodel.perplexity(tf))  # 收敛效果,perplexity:主题困惑度
        pic = pyLDAvis.sklearn.prepare(ldamodel, tf, tf_vectorizer, mds='mmds')
        pyLDAvis.display(pic)
        picpath = self.mainpath + '/' + 'lda_pass_before.html'
        pyLDAvis.save_html(pic, picpath)
        perplexity_result = self.perplexity_analyze(tf)
        topicpath = self.mainpath + '/' + 'topic_words_before'+self.chat_name+'.txt'
        n_top_words = 20  # 打印的主题词数  ---7
        tf_feature_names = tf_vectorizer.get_feature_names_out()
        self.print_top_words(ldamodel, tf_feature_names, n_top_words,topicpath,chat_names,perplexity_result)
