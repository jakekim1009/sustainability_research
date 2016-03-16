import numpy as np
from PIL import Image
import glob, os

dir1 = '/cvgl/u/rsluo/daytime/training/0_to_8'
dir2 = '/cvgl/u/rsluo/daytime/training/8_to_35'
dir3 = '/cvgl/u/rsluo/daytime/training/35_to_200'
dirs_list = [dir1, dir2, dir3]

for dir_idx, directory in enumerate(dirs_list):
	print "Starting directory " + str(dir_idx)
	image_count = 0
	for infile in glob.glob(directory + "/*.jpg"):
		dirname = os.path.dirname(infile)
		filename, ext = os.path.splitext(os.path.basename(infile))
		image = Image.open(infile)
		image90 = image.rotate(90)
		image90.save(dirname + "/" + str(int(float(filename) + 50000)) + ".jpg", "JPEG")
		image180 = image.rotate(180)
		image180.save(dirname + "/" + str(int(float(filename) + 100000)) + ".jpg", "JPEG")
		image270 = image.rotate(270)
		image270.save(dirname + "/" + str(int(float(filename) + 150000)) + ".jpg", "JPEG")
		if (image_count % 1000) == 0:
			print "Rotated " + str(image_count) + " images"
		image_count += 1
