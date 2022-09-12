import tensorflow.keras as keras


class preprocesser(object):

    def __init__(self, config):
        self.config = config

    def read_txt(self, txt_path):
        with open(txt_path, "r", encoding='utf-8') as f:
            data = f.readlines()
        labels = []
        contents = []
        for line in data:
            label, content = line.strip().split('\t')
            labels.append(label)
            contents.append(content)
        return labels, contents

    def get_vocab_id(self):
        vocab_path = self.config.get("data_path", "vocab_path")
        with open(vocab_path, "r", encoding="utf-8") as f:
            infile = f.readlines()
        vocabs = list([word.replace("\n", "") for word in infile])
        vocabs_dict = dict(zip(vocabs, range(len(vocabs))))
        return vocabs, vocabs_dict

    def get_category_id(self):
        categories = ["色情", "诈骗洗钱", "技术", "博彩", "刷粉刷量", "数据贩卖"]
        cates_dict = dict(zip(categories, range(len(categories))))
        return cates_dict

    def word2idx(self, txt_path, max_length):
        vocabs, vocabs_dict = self.get_vocab_id()
        cates_dict = self.get_category_id()
        labels, contents = self.read_txt(txt_path)
        labels_idx = []
        contents_idx = []

        # 遍历语料
        for idx in range(len(contents)):
            tmp = []
            labels_idx.append(cates_dict[labels[idx]])
            # 遍历contents中各词并将其转换为索引后加入contents_idx中
            for word in contents[idx]:
                if word in vocabs:
                    tmp.append(vocabs_dict[word])
                else:
                    tmp.append(5000)
            contents_idx.append(tmp)

        x_pad = keras.preprocessing.sequence.pad_sequences(contents_idx, max_length)
        y_pad = keras.utils.to_categorical(labels_idx, num_classes=len(cates_dict))

        return x_pad, y_pad

    def word2idx_for_sample(self, sentence, max_length):
        vocabs, vocabs_dict = self.get_vocab_id()
        result = []
        # 遍历语料
        for word in sentence:
            if word in vocabs:
                result.append(vocabs_dict[word])
            else:
                result.append(5000)

        x_pad = keras.preprocessing.sequence.pad_sequences([result], max_length)
        return x_pad

