import os
import uuid
import logging
import time
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import keras.backend.tensorflow_backend as KTF
from numpy import linalg as LA
# from indexer.logs import write_log

# # set keras default model path
# os.environ['KERAS_HOME'] = os.path.abspath(os.path.join('.', 'data'))

class Img2Vec(object):
    def __init__(self):
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.config.gpu_options.per_process_gpu_memory_fraction = 0.9
        self.session = tf.Session(config=self.config)
        set_session(self.session)
        self.graph = tf.get_default_graph()
        self.model = VGG16(
                    weights='imagenet',
                    include_top=False,
                    pooling='avg')


    def execute(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        with self.graph.as_default():
            with self.session.as_default():
                features = self.model.predict(x)
                norm_feature = features[0] / LA.norm(features[0])
                norm_feature = [i.item() for i in norm_feature]
                return norm_feature


    def __call__(self, img_list, ids_list):
        insert_img_list = []
        insert_ids_list = []

        for i in range(len(img_list)):
            try:
                insert_img_list.append(self.execute(img_list[i]))
                insert_ids_list.append(ids_list[i])
            except Exception as e:
                # write_log(e, 1)
                print("the img has broken:", img_list[i], e)
                continue
        return insert_img_list, insert_ids_list

def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if (f.endswith('.jpg') or f.endswith('.png'))]


if __name__ == '__main__':
    import os
    import time

    file_path = '../../test_pic'
    img_list = get_imlist(file_path)
    print(img_list)
    img_to_vec = Img2Vec()
    ids = []
    for i in range(len(img_list)):
        ids.append(i)

    s1 = time.time()
    norm_feat_list, ids = img_to_vec(img_list, ids)
    print(ids, len(norm_feat_list),len(norm_feat_list[0]))
    s2 = time.time()
    print('use time:', s2 - s1)
