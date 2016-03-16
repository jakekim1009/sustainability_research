import numpy as np
import os, sys

# Add Caffe python to path
CAFFE = '/cvgl/software/opt/caffe/'
caffe_python_path = os.path.join(CAFFE, 'python')
sys.path.insert(0, caffe_python_path)

import caffe
caffe.set_device(0)

model_file = '/cvgl/u/rsluo/vgg_cnn_f/architectures/VGG_F_trial1.prototxt
weights_file = '/cvgl/u/rsluo/vgg_cnn_f/snapshots/VGG_F_trial1__iter_280000.caffemodel
net = caffe.Net(model_file, weights_file, caffe.TEST)
num_examples = 30000

data_layer_name = 'data'
score_layer_name = 'pool6'

labels = []
preds = []
iterations = 0
while len(preds) < num_examples:
  iterations += 1
  print 'Iter: {}'.format(iterations)
  net.forward(end=score_layer_name)
  # Get test label
  label = net.blobs[data_layer_name].data
  labels.append(label)
  # Get class scores
  output = net.blobs[score_layer_name].data
  preds += list(output.squeeze())

preds = np.asarray(preds[:num_examples])
