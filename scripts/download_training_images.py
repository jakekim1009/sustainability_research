from rachel_utils import *
from neal_utils import *


class_bounds = [0, 8]
num_images = 10000

print 'Lower bound: {}'.format(class_bounds[0])
print 'Upper bound: {}'.format(class_bounds[1])
print 'Number of images: {}'.format(num_images)

sample_locations = sample_images_one_class(num_images, class_bounds)

##############################################################################################

'''

# Testing image sampling in NL range
out_dir = '/atlas/u/nj/viirs/daytime/test/35_to_200/'
num_images = 10000
nl_min = 35
nl_max = 200
locs_list_in = '/atlas/u/nj/viirs/daytime/class3_locs.pkl'
locs_list_out = '/atlas/u/nj/viirs/daytime/class3_locs.pkl'

print 'Lower bound: {}'.format(nl_min)
print 'Upper bound: {}'.format(nl_max)
print 'Number of images: {}'.format(num_images)
print 'Directory: {}'.format(out_dir)

locs_list = sample_images_in_nl_range(out_dir, num_images, nl_min, nl_max, locs_list_out, locs_list_in=locs_list_in)

'''

