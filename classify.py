# coding:utf-8
from __future__ import division
import time
import logging
import sys
caffe_root = '/home/yanlei/caffe/'
sys.path.insert(0, caffe_root + 'python')
import caffe

from PyQt4.QtGui import *
from PyQt4.QtCore import *


logging.getLogger('flower classify')
logging.basicConfig(level=logging.INFO)

labels = ['pink primrose', 'hard-leaved pocket orchid', 'canterbury bells',
          'sweet pea', 'english marigold', 'tiger lily', 'moon orchid',
          'bird of paradise', 'monkshood', 'globe thistle', 'snapdragon',
          "colt's foot", 'king protea', 'spear thistle', 'yellow iris',
          'globe-flower', 'purple coneflower', 'peruvian lily', 'balloon flower',
          'giant white arum lily', 'fire lily', 'pincushion flower', 'fritillary',
          'red ginger', 'grape hyacinth', 'corn poppy', 'prince of wales feathers',
          'stemless gentian', 'artichoke', 'sweet william', 'carnation', 'garden phlox',
          'love in the mist', 'mexican aster', 'alpine sea holly', 'ruby-lipped cattleya',
          'cape flower', 'great masterwort', 'siam tulip', 'lenten rose', 'barbeton daisy',
          'daffodil', 'sword lily', 'poinsettia', 'bolero deep blue', 'wallflower',
          'marigold', 'buttercup', 'oxeye daisy', 'common dandelion', 'petunia',
          'wild pansy', 'primula', 'sunflower', 'pelargonium', 'bishop of llandaff',
          'gaura', 'geranium', 'orange dahlia', 'pink-yellow dahlia?', 'cautleya spicata',
          'japanese anemone', 'black-eyed susan', 'silverbush', 'californian poppy',
          'osteospermum', 'spring crocus', 'bearded iris', 'windflower', 'tree poppy',
          'gazania', 'azalea', 'water lily', 'rose', 'thorn apple', 'morning glory',
          'passion flower', 'lotus', 'toad lily', 'anthurium', 'frangipani', 'clematis',
          'hibiscus', 'columbine', 'desert-rose', 'tree mallow', 'magnolia', 'cyclamen ',
          'watercress', 'canna lily', 'hippeastrum ', 'bee balm', 'ball moss', 'foxglove',
          'bougainvillea', 'camellia', 'mallow', 'mexican petunia', 'bromelia', 'blanket flower',
          'trumpet creeper', 'blackberry lily']


class FlowerClassifier(QThread):
    result_signal = pyqtSignal(dict)
    image_path_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        logging.info("Initializing FlowerClassifier network")
        model = 'deploy1.prototxt'
        weights = 'snapshot_iter_30000_finetune.caffemodel'
        self.net = caffe.Net(model, weights, caffe.TEST)
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2, 0, 1))
        self.transformer.set_channel_swap('data', (2, 1, 0))
        self.transformer.set_raw_scale('data', 255)
        self.net.blobs['data'].reshape(1, 3, 227, 227)
        self.image_to_recognition = list()

    def classify(self, image_path):
        self.image_path_signal.emit(image_path)
        # logging.info("classify image")
        try:
            start = time.time()
            image = caffe.io.load_image(image_path)
            self.net.blobs['data'].data[...] = self.transformer.preprocess('data', image)
            self.net.forward()
            prob = self.net.blobs['prob'].data[0]
            top_k = self.net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
            end = time.time()
            top_prob = [prob[index] for index in top_k]
            # logging.info("Time cost: {0}".format(end - start))
            result = list()
            for i in range(len(top_k)):
                item = {"label": labels[top_k[i]], "prob": top_prob[i]}
                result.append(item)
            results = {"result": result, "time": end-start}
            self.result_signal.emit(results)
        except IOError as e:
            print e

    def run(self):
        if self.image_to_recognition:
            for image in self.image_to_recognition:
                self.classify(image)

    def set_image(self, images):
        self.image_to_recognition = images
