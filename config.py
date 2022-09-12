class Config:
    def __init__(self):
        self.mongo={"host": "localhost","port":27017,"db":"localhost"}
        self.group={"id":124,"name":"不知道群","rtable":"r124","table":"t124"}
        self.userid=''
        self.header = ["id", "latest", "topic", "per", "loc", "org", "time", "contact", "frequency", "groupinfo"]
        self.l_header=["topic", "per", "loc", "org", "time", "contact"]
        self.categories = ["色情", "诈骗洗钱", "技术", "博彩", "刷粉刷量", "数据贩卖"]
        self.config_dict = {
            "data_path": {
                "vocab_path": "data/vocab.txt",
                "trainingSet_path": "data/train.txt",
                "valSet_path": "data/val.txt",
                "testingSet_path": "data/test.txt"
            },
            "CNN_training_rule": {
                "embedding_dim": 64,
                "seq_length": 300,
                "num_classes": 6,

                "conv1_num_filters": 128,
                "conv1_kernel_size": 1,

                "conv2_num_filters": 64,
                "conv2_kernel_size": 1,

                "vocab_size": 5050,

                "hidden_dim": 128,

                "dropout_keep_prob": 0.5,
                "learning_rate": 1e-3,

                "batch_size": 64,
                "epochs": 30,

                "print_per_batch": 100,
                "save_per_batch": 1000
            },
            "result": {
                "CNN_model_path": "data/model/CNN_model.h5"
            }
        }

    def get(self, section, name):
        return self.config_dict[section][name]