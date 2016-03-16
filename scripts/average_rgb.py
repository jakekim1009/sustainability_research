import numpy as np
from scipy import misc
from PIL import Image
import glob, os

dir1 = '/cvgl/u/rsluo/daytime/training/0_to_8'
dir2 = '/cvgl/u/rsluo/daytime/training/8_to_35'
dir3 = '/cvgl/u/rsluo/daytime/training/35_to_200'
dirs_list = [dir1, dir2, dir3]

r = 0
g = 0
b = 0
num_pixels = 0

for dir_idx, directory in enumerate(dirs_list):
	print "Starting directory " + str(dir_idx)
	
	image_count = 0
	
	for infile in glob.glob(directory + "/*.jpg"):
		file, ext = os.path.splitext(infile)
		image = Image.open(infile)
		width, height = image.size

		pixels = misc.imread(infile)

		r += np.sum(pixels[:,:,0])
		g += np.sum(pixels[:,:,1])
		b += np.sum(pixels[:,:,2])

		num_pixels += width * height
		image_count += 1
		
		if (image_count % 20000) == 0:
			print "Processed " + str(image_count) + " images in this directory"

r_avg = r/num_pixels
g_avg = g/num_pixels
b_avg = b/num_pixels

text_file = open("average_rgb_value.txt", "w")
text_file.write("Average r: " + str(r_avg) + "\n")
text_file.write("Average g: " + str(g_avg) + "\n")
text_file.write("Average b: " + str(b_avg) + "\n")

print "Average r: " + str(r_avg)
print "Average g: " + str(g_avg)
print "Average b: " + str(b_avg)
