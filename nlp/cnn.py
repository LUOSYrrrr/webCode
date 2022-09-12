import numpy as np
import os
import tensorflow.keras as keras
from utils.preprocess import preprocesser


class TextCNN():
    def __init__(self, config):
        self.config = config
        self.pre = preprocesser(config)
        self.nums = [0, 0, 0, 0, 0, 0]
        model_save_path = self.config.get("result", "CNN_model_path")
        print(model_save_path)
        self.model = keras.models.load_model(model_save_path)
        self.categories=self.config.categories
        self.seq_length = self.config.get("CNN_training_rule", "seq_length")

    def predict(self, words):
        words = ''.join(words)
        x_test = self.pre.word2idx_for_sample(words, max_length=self.seq_length)
        pre_test = self.model.predict(x_test)
        # print(pre_test)
        label = self.categories[np.argmax(pre_test)]
        self.nums[self.categories.index(label)] += 1
        return label
