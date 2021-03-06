import glob
import numpy as np
import time

train_dir1 = '/atlas/u/nj/viirs/daytime/training/0_to_8/'
train_dir2 = '/atlas/u/nj/viirs/daytime/training/8_to_35/'
train_dir3 = '/atlas/u/nj/viirs/daytime/training/35_to_200/'

test_dir1 = '/atlas/u/nj/viirs/daytime/test/0_to_8/'
test_dir2 = '/atlas/u/nj/viirs/daytime/test/8_to_35/'
test_dir3 = '/atlas/u/nj/viirs/daytime/test/35_to_200/'

train_fn = '../data/training_images_labeled.txt'
test_fn = '../data/test_images_labeled.txt'

# Create text file with training image paths and labels
with open(train_fn, 'w') as train_file:
    for image_fn in glob.glob(train_dir1 + '*'):
        data = image_fn + ' 0\n'
        train_file.write(data)
    for image_fn in glob.glob(train_dir2 + '*'):
        data = image_fn + ' 1\n'
        train_file.write(data)
    for image_fn in glob.glob(train_dir3 + '*'):
        data = image_fn + ' 2\n'
        train_file.write(data)

# Create text file with test image paths and labels
with open(test_fn, 'w') as test_file:
    for image_fn in glob.glob(test_dir1 + '*'):
        data = image_fn + ' 0\n'
        test_file.write(data)
    for image_fn in glob.glob(test_dir2 + '*'):
        data = image_fn + ' 1\n'
        test_file.write(data)
    for image_fn in glob.glob(test_dir3 + '*'):
        data = image_fn + ' 2\n'
        test_file.write(data)


