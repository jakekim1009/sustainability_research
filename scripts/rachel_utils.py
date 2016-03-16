import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import bisect
import os
import time
from neal_utils import *

##############################################################################################


def get_year_avg (month_avgs, obs_count):
	"""
	Calculates the yearly average light intensity

	Inputs:
	- month_avgs: The average monthly nighttime light intensity. Shape (num_pixels_x, num_pixels_y, num_months=12)
	- obs_count: The number of times a nightlight intensity observation was made at each location each month. Shape (num_pixels_x, num_pixels_y, num_months=12)

	Returns:
	- year_avgs: The yearly average nighttime light intensity. Shape (num_pixels_x, num_pixels_y). Locations with zero observations are set to -1000.
	- num_observations: The total number of observations at each location.
	"""
	num_months = month_avgs.shape[2]
	year_avgs = np.zeros(obs_count[:,:,0].shape)

	for i in xrange(num_months):
		year_avgs += month_avgs[:, :, i] * obs_count[:, :, i]

	num_observations = np.sum(obs_count, axis=2)

	# Prevent divide by zero error
	zero_obs = np.zeros_like(num_observations)
	zero_obs[num_observations == 0] = 1
	year_avgs /= (num_observations + zero_obs)
	year_avgs[num_observations == 0] = -1000
	return year_avgs, num_observations


##############################################################################################


def plot_histogram(night_intensities):
	"""
	Plots a histogram given a set of data points

	Inputs:
	- night_intensities: an array of the nighttime light intensities at all locations in Africa

	Returns:
	- min_intensity: The lowest nighttime light intensity 
	- mean: The mean nighttime light intensity
	- max_intensity: The highest nighttime light intensity
	"""
	plt.hist(night_intensities)
	min_intensity = np.min(night_intensities)
	max_intensity = np.max(night_intensities)
	mean = np.mean(night_intensities)
	return min_intensity, mean, max_intensity


##############################################################################################


def sample_images(num_images, class_bounds):
	"""
	Samples the specified number of images from each class, yielding a balanced number of samples from each class

	Inputs:
	- num_images: The number of images that we want from each class
	- class_bounds: An array of class boundaries. The first element of this array is the lowest nighttime light intensity value, and the last element of the array is the highest nighttime light intensity value.

	Returns:
	- sample_locations: An array of (lat, long, class, intensity) tuples corresponding to locations for which we want to get the daytime satellite images. 
	"""
	min_lat = -40
	max_lat = 40
	min_long = -20
	max_long = 60

	num_classes = len(class_bounds) - 1
	class_count = np.zeros(num_classes)

	sample_locations = []
	total_samples = num_classes * num_images

	tile2 = np.load('/atlas/u/nj/viirs/2015/data/tile2_obs.npy')
	tile5 = np.load('/atlas/u/nj/viirs/2015/data/tile5_obs.npy')
	tile2dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/2/SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')
	tile5dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/5/SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')

	while (len(sample_locations) < total_samples):
		my_lats = np.random.uniform(min_lat, max_lat, total_samples) #total_samples - len(sample_locations))
		my_longs = np.random.uniform(min_long, max_long, total_samples) #total_samples - len(sample_locations))
		my_locations = [[my_lats[i], my_longs[i]] for i in range (len(my_lats))]

		# Check if lat, long pairs are within Africa bounding box
		in_africa = check_batch_within_africa(my_lats, my_longs)

		for i in range(len(in_africa)):
			if in_africa[i]:
				my_intensity = lat_lon_to_NL_array_input([my_locations[i]], tile2, tile5, tile2dir, tile5dir)[0][2]
				which_class = bisect.bisect(class_bounds, my_intensity)

				# Check if this image contributes to balanced classes
				if class_count[which_class-1] < num_images:
					filepath = "../images/" + str(class_bounds[which_class-1]) + "_to_" + str(class_bounds[which_class]) 
					filename = filepath + "/" + str(int(class_count[which_class-1])) + ".jpg"
					# Create a folder for this class
					try:
						os.makedirs(filepath)
					except OSError:
						if not os.path.isdir(filepath):
							raise
					if sample_image(filename, my_lats[i], my_longs[i], zoom=17):
						sample_locations.append((my_lats[i], my_longs[i], which_class, my_intensity))
						class_count[which_class-1] += 1

				if len(sample_locations) == total_samples:
					break

	return sample_locations

##############################################################################################

def lat_long_to_pixel(geotif_addr, lat_long_pairs):
	# Load the image dataset
	ds = gdal.Open(geotif_addr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srs_lat_long = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srs_lat_long,srs)
	# Go through all the point pairs and translate them to latitude/longitude pairings
	pixel_pairs = []
	for point in lat_long_pairs:
		# Change the point locations into the GeoTransform space
		(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
		# Translate the x and y coordinates into pixel values
		x = (point[1]-gt[0])/gt[1]
		y = (point[0]-gt[3])/gt[5]
		# Add the point to our return array
		pixel_pairs.append([int(x),int(y)])
	return pixel_pairs

##############################################################################################

#Returns a list of (latitude, longitude, intensity) tuple
def lat_long_to_intensities_batch(lat_long_list, tile2, tile5, tile2dir, tile5dir):

	# Transposes array so it's like the tiles
	tile2 = tile2.T
	tile5 = tile5.T

	# Splits list into separate lists for each tile
	lat_long_list_tile2 = [x for x in lat_long_list if x[0]>=0]
	lat_long_list_tile5 = [x for x in lat_long_list if x[0]<0]
	
	# Convert lat/long lists to pixel lists
	pixels_tile2 = lat_long_to_pixel(tile2dir, lat_long_list_tile2)
	pixels_tile5 = lat_long_to_pixel(tile5dir, lat_long_list_tile5)

	# Make sure pixel values are within tile
	tile2_x, tile2_y = tile2.shape
	tile5_x, tile5_y = tile5.shape
	for i in xrange(len(pixels_tile2)):
		if pixels_tile2[i][0] >= tile2_x:
			pixels_tile2[i][0] = tile2_x - 1
		if pixels_tile2[i][1] >= tile2_y:
			pixels_tile2[i][1] = tile2_y - 1
	for i in xrange(len(pixels_tile5)):
		if pixels_tile5[i][0] >= tile5_x:
			pixels_tile5[i][0] = tile5_x - 1
		if pixels_tile5[i][1] >= tile5_y:
			pixels_tile5[i][1] = tile5_y - 1

	intensities_tile2 = []
	intensities_tile5 = []
	for i in xrange(len(pixels_tile2)):
		intensities_tile2.append(tile2[pixels_tile2[i][0], pixels_tile2[i][1]])
	for i in xrange(len(pixels_tile5)):
		intensities_tile5.append(tile5[pixels_tile5[i][0], pixels_tile5[i][1]])

	intensities = intensities_tile2 + intensities_tile5

	return intensities

##############################################################################################

def sample_images_one_class(total_samples, class_bounds):
	"""
	Samples the specified number of images from one given class

	Inputs:
	- total_samples: The number of images that we want from this class
	- class_bounds: An array of the class boundaries. The first element of this array is the lowest nighttime light intensity value, and the last element of the array is the highest nighttime light intensity value.

	Returns:
	- sample_locations: An array of (lat, long, intensity) tuples corresponding to locations for which we want to get the daytime satellite images. 
	"""
	min_lat = -40
	max_lat = 40
	min_long = -20
	max_long = 60

	# List of lat/long/intensity tuples
	sample_locations = []

	# Loading tiles
	tile2 = np.load('/atlas/u/nj/viirs/2015/data/tile2_obs.npy')
	tile5 = np.load('/atlas/u/nj/viirs/2015/data/tile5_obs.npy')
	tile2dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/2/SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')
	tile5dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/5/SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')

	# Sets image directory
	filepath = "/atlas/u/nj/viirs/daytime/test/" + str(class_bounds[0]) + "_to_" + str(class_bounds[1]) + '/'

	# Determines name of next image
	next_idx = determine_next_image_fn(filepath)

	t0 = time.time()
	while (len(sample_locations) < total_samples):
		# Randomly chooses locations
		my_lats = np.random.uniform(min_lat, max_lat, total_samples)
		my_longs = np.random.uniform(min_long, max_long, total_samples)

		# Check if lat, long pairs are within Africa bounding box
		in_africa = check_batch_within_africa(my_lats, my_longs)
		my_lats = my_lats[in_africa]
		my_longs = my_longs[in_africa]

		# Make list of locations that are within Africa
		my_locations = [[my_lats[i], my_longs[i]] for i in range (len(my_lats))]
		my_intensities = lat_long_to_intensities_batch(my_locations, tile2, tile5, tile2dir, tile5dir)
		print 'My locations length: {}'.format(len(my_locations))
		print 'My intensities length: {}'.format(len(my_intensities))

		if my_locations:
			for idx, my_location in enumerate(my_locations):
				# Finding NL value corresponding to location
				my_intensity = my_intensities[idx]
				# Boolean for whether or not NL value is in right class
				in_class = (my_intensity >= class_bounds[0]) and (my_intensity < class_bounds[1])

				if in_class:
					print my_intensity
					filename = filepath + str(int(len(sample_locations)) + next_idx) + ".jpg"
					# Try to sample image
					if sample_image(filename, my_location[0], my_location[1], zoom=17):
						sample_locations.append((my_location[0], my_location[1], my_intensity))

						# Printing updates
						if len(sample_locations) % 100 == 0:
							print 'Downloaded {} images so far: {} seconds elapsed'.format(len(sample_locations), time.time() - t0)

				if len(sample_locations) >= total_samples:
					break

	return sample_locations

##############################################################################################


def sample_images_within_class(num_images, class_bounds):
	"""
	Samples the specified number of images by randomly selecting pixel locations from just within each class

	Inputs:
	- num_images: The number of images that we want from each class
	- class_bounds: An array of class boundaries. The first element of this array is the lowest nighttime light intensity value, and the last element of the array is the highest nighttime light intensity value.

	Returns:
	- sample_locations: An array of (lat, long, class, intensity) tuples corresponding to locations for which we want to get the daytime satellite images. 
	"""

	num_classes = len(class_bounds) - 1
	class_count = np.zeros(num_classes)

	sample_locations = []
	total_samples = num_classes * num_images

	tile2 = np.load('/atlas/u/nj/viirs/2015/data/tile2_obs.npy')
	tile5 = np.load('/atlas/u/nj/viirs/2015/data/tile5_obs.npy')
	tile2dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/2/SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')
	tile5dir = os.path.abspath('/atlas/u/nj/viirs/2015/12/5/SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif')

	# Create an array with (intensity, tile # (either 2 or 5), pixel row, pixel column) tuples
	nl_array = np.array([(tile2[row][col], 2, row, col) for row in range(tile2.shape[0]) for col in range(tile2.shape[1])])
	nl_array.extend([(tile5[row][col], 5, row, col) for row in range(tile5.shape[0]) for col in range(tile5.shape[1])])

	print nl_array.shape

	#nl_array = [(intensity, 2, intensity.index[0], intensity.index[1]) for line in tile2 for intensity in np.split(line, len(line))]
	#nl_array.extend([(intensity, 5, intensity.index[0], intensity.index[1]) for line in tile5 for intensity in np.split(line, len(line))])
	# Keep only the locations that are actually in Africa
	## TO DO ##

	for i in range(num_classes):
		print i
		# All pixel intensities and locations for which the nighttime light intensity is within a certain class
		nl_within_class = nl_array[(nl_array[0] >= class_bounds[i]) and (nl_array[0] < class_bounds[i+1])]
		# Ramdomly pick num_images of the samples
		nl_samples = random.sample(nl_within_class, num_images)

		my_lats = [pixel_to_lat_lon(tile2dir, [sample[2], sample[3]])[0] for sample in nl_samples if (sample[1] == 2)]
		my_lats.extend([pixel_to_lat_lon(tile5dir, [sample[2], sample[3]])[0] for sample in nl_samples if (sample[1] == 5)])
		my_longs = [pixel_to_lat_lon(tile2dir, [sample[2], sample[3]])[1] for sample in nl_samples if (sample[1] == 2)]
		my_longs.extend([pixel_to_lat_lon(tile5dir, [sample[2], sample[3]])[1] for sample in nl_samples if (sample[1] == 5)])

		filepath = "../images/" + str(class_bounds[i]) + "_to_" + str(class_bounds[i+1]) 
		filename = filepath + "/" + str(int(class_count[i])) + ".jpg"
		# Create a folder for this class
		try:
			os.makedirs(filepath)
		except OSError:
			if not os.path.isdir(filepath):
				raise

		# Download the images
		for j in range(len(nl_samples)):
			if sample_image(filename, my_lats[j], my_longs[j], zoom=17):
				sample_locations.append((my_lats[j], my_longs[j], i+1, nl_samples[j][0]))
				class_count[i] += 1

	return sample_locations
