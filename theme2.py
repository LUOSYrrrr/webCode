"""
将mongo中处理后的数据（已分词）进一步进行主题挖掘

运行完主题1进行分析后，只需要修改主题数（标号为”8“处）

"""
import string
import pymongo
from sklearn.decomposition import LatentDirichletAllocation
from \
        sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pyLDAvis.sklearn
import wordcloud
import jieba
class theme2():
    def __init__(self, group):
        self.punctuation_string = string.punctuation  # 用于预处理标点
        self.group = group
        self.chat_name = group['rtable']  # 逐条消息存储的数据库表名  ---2

        self.mainpath = 'static/themeResult'  # 其他处理结果所在文件夹 ---1

        # 数据库准备
        self.client = pymongo.MongoClient('localhost', 27017)  # 建立连接，一般默认
        self.db = self.client['localhost']  # 引号内为数据库的名字（原始群聊消息）  ---2

        self.chat_collection = self.db['row_chat']  # 需要进行主题挖掘的数据(已分词)所在表
        self.topic_collection = self.db['topics_final']  # 将多个群聊对话进行主题挖掘后存放的表  ---3



    #################
    # 从mongo数据库中获取数据，得到含每个群聊消息的列表
    # create_word_list1():分析指定群
    # create_word_list1():分析所有群
    def create_word_list1(self):
        chat_list = []
        print(self.chat_name)
        name_list = [self.chat_name]  # 需要进行主题挖掘的群 ---5

        names = ''
        for name in name_list:
            names += name
            print(names)
            myquery = {"chat_name": name}
            msg = self.chat_collection.find({"chat_name": self.chat_name})

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
        return tf_train, tf_vectorizer_train


    # tf, tf_vectorizer = verctotizer_train()
    #
    # ########################
    # # LDA主题模型
    # # 训练模型↓
    # # --------------
    # n_topics = 3  # 主题数量，自定义，可以根据困惑度和可视化结果进行调整  ---8
    # ldamodel = LatentDirichletAllocation(n_components=n_topics, max_iter=50,  # 迭代数量：50
    #                                      learning_method='batch',
    #                                      #                                 doc_topic_prior=0.1,  # α，不定义时默认位1/主题数
    #                                      #                                 topic_word_prior=0.01,  # β，不定义时默认位1/主题数
    #                                      random_state=0)


    # 通过fit_transform函数，我们就可以得到文档的主题模型分布在ldaresult中
    # 而主题词分布则在ldamodel.components_中
    # ldaresult = ldamodel.fit_transform(tf)
    def lda_train(self,ldamodel,tf):
        result = ldamodel.fit_transform(tf)
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
    # picpath = mainpath + '/' + 'lda_pass_final.html'
    # pyLDAvis.save_html(pic, picpath)
    #
    # ########################
    # # 打印对应主题下的前n_top_words个关键词，并写入文档topic-words.txt
    # topicpath = mainpath + '/' + 'topic_words_final.txt'


    def print_top_words(self,model, feature_names, n_words,topicpath,chat_names,ldaresult):
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

        data = {'name': chat_names, 'topic_words': words, 'result': str(ldaresult),'flag':0}
        self.topic_collection.delete_many({'name': chat_names})
        self.topic_collection.insert_one(data)
        ff.close()


    # n_top_words = 20  # 打印的主题词数  ---7
    # tf_feature_names = tf_vectorizer.get_feature_names_out()
    # print_top_words(ldamodel, tf_feature_names, n_top_words)

    # import wordcloud
    # import jieba


    def wordclouds(self,filepath):
        file = open(filepath, 'r', encoding='utf-8')
        index = 1
        for line in file:
            w = wordcloud.WordCloud(width=1000, font_path="NotoSerifCJK-Bold.ttc", height=700)
            w.generate(" ".join(jieba.lcut(line)))
            wordcloudpath = self.mainpath+'/cloud' + '/' + 'topic{}cloud'+self.chat_name+'.png'.format(index)
            w.to_file(wordcloudpath.format(index))
            index += 1


   # wordclouds(topicpath)

    def runTheme2(self):
        lda_word_list, chat_names = self.create_word_list1()
        tf, tf_vectorizer = self.verctotizer_train(lda_word_list)

        ########################
        # LDA主题模型
        # 训练模型↓
        # --------------
        n_topics = 1  # 主题数量，自定义，可以根据困惑度和可视化结果进行调整  ---8
        ldamodel = LatentDirichletAllocation(n_components=n_topics, max_iter=50,  # 迭代数量：50
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
        picpath = 'templates' + '/' + 'lda_pass_final'+self.chat_name+'.html'
        pyLDAvis.save_html(pic, picpath)

        ########################
        # 打印对应主题下的前n_top_words个关键词，并写入文档topic-words.txt
        topicpath = self.mainpath + '/' + 'topic_words_final'+self.chat_name+'.txt'
        n_top_words = 20  # 打印的主题词数  ---7
        tf_feature_names = tf_vectorizer.get_feature_names_out()
        self.print_top_words(ldamodel, tf_feature_names, n_top_words, topicpath, chat_names,ldaresult)
        self.wordclouds(topicpath)


