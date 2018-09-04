# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from cnn_model import TCNNConfig, TextCNN
from data.cnews_loader import read_category, read_vocab

try:
    bool(type(unicode))
except NameError:
    unicode = str

base_dir = 'data/yidong'
vocab_dir = os.path.join(base_dir, 'vocab.txt')

save_dir = 'checkpoints/textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.categories, self.cat_to_id = read_category()
        self.words, self.word_to_id = read_vocab(vocab_dir)
        self.config.vocab_size = len(self.words)
        self.model = TextCNN(self.config)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, message):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        return self.categories[y_pred_cls[0]]

    def deal_test(self,filename):
        '''处理短文本的预测数据

        input：IntentTestA_20000001  {"sentence": "设置打电话的来电铃声"}
        output:id,设置打电话的来电铃声       预测后得到:id+/t+label1
        '''
        results=[]
        out = open(filename,'a+',encoding='utf-8-sig')
        with open("data/intent_data.test.txt",'r',encoding='utf=8') as f:
            for line in f:
                id, dict = line.split('\t')
                for v in eval(dict).values():
                    #print(v)
                    results.append(id+'\t'+self.predict(v))
            for result in  results:
                out.write(result+'\n')

if __name__ == '__main__':
    cnn_model = CnnModel()
   #  test_demo = ['我要查询我的这个密码',
   #               '怎么开通夜间流量包',
		 #  '拜拜了就这样吧'
		 # ]
   #  for i in test_demo:
   #      print(cnn_model.predict(i),i)
    cnn_model.deal_test('result_action.txt')