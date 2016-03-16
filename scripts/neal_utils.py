import cv2
import numpy as np
import os
import time
import urllib
import json
import pickle as pkl
import glob
import random
from PIL import Image
from shapely.geometry import Point, Polygon
from osgeo import gdal, osr
from jake_utils import *

##############################################################################################

def sample_image(out_fn, lat, lon, height=400, width=400, zoom=17):
  """
  This function uses the Google Static Maps API to download and save one satellite image.
  :param out_fn: Output filename for saved image
  :param lat: Latitude of image center
  :param lon: Longitude of image center
  :param height: Height of image in pixels
  :param width: Width of image in pixels
  :param zoom: Zoom level of image
  :return: True if valid image saved, False if no image saved
  """
  # Google Static Maps API key
  keys = ["AIzaSyDzWmvcVKeyoDgyvnLgHpVnCLpypWLrkPY", "AIzaSyBW1imRBOtaa6uwvVRxjlaZ38U0rkjbYzM",
          "AIzaSyAejgapvGncLMRiMlUoqZ2h6yRF-lwNYMM", "AIzaSyD3f6sozQ3UqlP45Oj_8plnc5KILYC9amU",
          "AIzaSyAZlsqwvlFBArKqMCbPfE_BMVL_KU6dKSM", "AIzaSyCkRXcAdW-rwh7cpqOOrJBw2agkeftdcDc",
          "AIzaSyCzbSnF_OH2sElz1Mh2xuU0XLaF0oI3DxE", "AIzaSyDvzkEGJRZY53JnnFPnloqNz-4C_6XIhas",
          "AIzaSyAuuN1he9LOTlXR5X3U3PatWsgW0E70kqg"]
  # Pick key at random
  key = np.random.randint(0,9)
  api_key = keys[key]
    
  try:
    # Save extra tall satellite image
    height_buffer = 100
    url_pattern = 'https://maps.googleapis.com/maps/api/staticmap?center=%0.6f,%0.6f&zoom=%s&size=%sx%s&maptype=satellite&key=%s'
    url = url_pattern % (lat, lon, zoom, width, height + height_buffer, api_key)
    urllib.urlretrieve(url, out_fn)

    # Cut out text at the bottom of the image
    image = cv2.imread(out_fn)
    image = image[(height_buffer/2):(height+height_buffer/2),:,:]
    cv2.imwrite(out_fn, image)

    # Check file size and delete invalid images < 10kb
    fs = os.stat(out_fn).st_size
    if fs < 10000:
      os.remove(out_fn)
      return False
    else:
      return True

  except:
    return False

##############################################################################################

def check_within_africa(lat, lon):
  """
  This function checks to see if a point is within Africa.
  :param lat: Latitude
  :param lon: Longitude
  :return: True if point is within Africa, False if not
  """
  # Load Africa Shapely polygon
  polygon_fn = '../data/shapefiles/africa.pkl'
  africa_polygon = pkl.load(open(polygon_fn, 'rb'))

  # Check location
  point = Point(lon, lat)
  return africa_polygon.contains(point)

##############################################################################################

def check_batch_within_africa(lats, lons):
  """
  This function checks arrays of lat/lon locations to see if they are within Africa and returns a list of booleans.
  :param lats: N lats to check
  :param lons: N lons to check
  :return: Length N array of booleans indicating if points are within Africa
  """
  t0 = time.time()
  N = lats.size
  within = np.zeros_like(lats)
  # Calculate max and min lat in batch
  max_lat = lats.max()
  min_lat = lats.min()

  # Create appropriate Africa Shapely polygon
  africa_polygon = create_africa_partial_polygon(max_lat, min_lat)

  for i in xrange(N):
    point = Point(lons[i], lats[i])
    within[i] = africa_polygon.contains(point)
    if (i + 1) % 100000 == 0:
      print 'Checked {} points: {} seconds'.format(i + 1, time.time() - t0)

  return within.astype(bool)


##############################################################################################

def get_year_avg(month_avgs, obs_count):
  """
  Calculates the yearly average light intensity

  Inputs:
  - month_avgs: The average monthly nighttime light intensity. Shape (num_pixels_x, num_pixels_y, num_months=12)
  - obs_count: The number of times a nightlight intensity observation was made at each location each month. Shape (num_pixels_x, num_pixels_y, num_months=12)

  Returns:
  - year_avgs: The yearly average nighttime light intensity. Shape (num_pixels_x, num_pixels_y)
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

def pixel_to_lat_lon(geotif_addr, pixel_pairs):
  """
  Translates pixel locations into latitude/longitude locations on a GEOTIF.
  :param geotif_addr: File location of GEOTIF
  :param pixel_pairs: Pixel pairs as a list of tuples in the form [(x1, y1), (x2, y2)]
  :returns: Lat/lon translations as a list of tuples in the form [(lat1, lon1), (lat2, lon2)]
  """
  # Load the image dataset
  ds = gdal.Open(geotif_addr)
  # Get a geo-transform of the dataset
  gt = ds.GetGeoTransform()
  # Create a spatial reference object for the dataset
  srs = osr.SpatialReference()
  srs.ImportFromWkt(ds.GetProjection())
  # Set up the coordinate transformation object
  srs_lat_long = srs.CloneGeogCS()
  ct = osr.CoordinateTransformation(srs, srs_lat_long)
  # Go through all the point pairs and translate them to pixel pairings
  lat_lon_pairs = []
  for point in pixel_pairs:
    # Translate the pixel pairs into untranslated points
    ulon = point[0]*gt[1]+gt[0]
    ulat = point[1]*gt[5]+gt[3]

    # Transform the points to the space
    (lon, lat, holder) = ct.TransformPoint(ulon, ulat)
    # Add the point to our return array
    lat_lon_pairs.append((lat, lon))
 
  return lat_lon_pairs

##############################################################################################

def make_pixel_pairs(low_x, high_x, low_y, high_y):
  """
  Returns a list of pixel pair tuples within the specified bounding box.
  """
  pixel_pairs = []
  for j in xrange(low_y, high_y):
    for i in xrange(low_x, high_x):
      pixel_pairs.append((i,j))
  return pixel_pairs

##############################################################################################

def convert_latlon_pairs_to_arrays(lat_lon_pairs):
  """
  Takes in a list of lat/lon tuples and returns arrays of the lats and lons.
  """
  lats = []
  lons = []
  for lat_lon in lat_lon_pairs:
    lats.append(lat_lon[0])
    lons.append(lat_lon[1])
  lats = np.array(lats)
  lons = np.array(lons)
  return lats, lons

##############################################################################################

def save_africa_partial_polygon(out_fn, top_lat, bottom_lat):
  """
  Saves slices of the Africa Shapely polygon.
  """
  polygon = create_africa_partial_polygon(top_lat, bottom_lat)

  # Save output polygon
  pkl.dump(polygon, open(out_fn, 'wb'))

##############################################################################################

def create_africa_partial_polygon(top_lat, bottom_lat):
  """
  Creates slices of the Africa Shapely polygon.
  """
  # Load full Africa Shapely polygon
  polygon_fn = '../data/shapefiles/africa.pkl'
  africa_polygon = pkl.load(open(polygon_fn, 'rb'))

  # Make top block polygon
  ring_points = [(-60, 75), (60, 75), (60, top_lat + 0.01), (-60, top_lat + 0.01)]
  top_polygon = Polygon(ring_points)
  # Make bottom block polygon
  ring_points = [(-60, bottom_lat - 0.01), (60, bottom_lat - 0.01), (60, -65), (-60, -65)]
  bottom_polygon = Polygon(ring_points)

  # Cut off top and bottom blocks
  polygon = africa_polygon.difference(top_polygon)
  polygon = polygon.difference(bottom_polygon)

  return polygon

##############################################################################################

def sample_images_in_nl_range(out_dir, num_images, nl_min, nl_max, locs_list_out, locs_list_in=None, height=400, width=400, zoom=17):
  """
  Samples specified number of images within a certain nightlights range and saves them in the output directory.
  :param out_dir: Directory to save images in
  :param num_images: Number of images to save
  :param nl_min: Minimum nightlights value
  :param nl_max: Maximum nightlights value
  """
  # Determine the next image filename
  next_idx = determine_next_image_fn(out_dir)

  # Create list of lat/lon locations that are within range (or load previously saved list)
  if locs_list_in is None:
    locs_list = find_locations_within_nl_range(nl_min, nl_max)
  else:
    locs_list = pkl.load(open(locs_list_in, 'rb'))

  # Shuffle list of locations
  random.shuffle(locs_list)

  # Save specified number of images
  locs_list = sample_images_from_list(out_dir, num_images, next_idx, locs_list, locs_list_out, height, width, zoom)

  # Return list of locations
  return locs_list

##############################################################################################

def sample_images_from_list(out_dir, num_images, next_idx, locs_list, locs_list_out, height=400, width=400, zoom=17):
  """
  Samples specified number of images from a list of locations and saves them in the output directory.
  """
  # Increment image filename if successful
  image_count = 0
  t0 = time.time()
  while image_count < num_images:
    image_fn = out_dir + str(next_idx) + '.jpg'
    got_image = False
    while not got_image:
      # Get next location
      lat, lon = locs_list.pop(0)
      # Try to get image
      got_image = sample_image(image_fn, lat, lon, height, width, zoom)
      '''
      if got_image:
        # Also get zoomed out image
        got_big_image = sample_image(image_fn[:-4] + '_big.jpg', lat, lon, height, width, zoom=13)
      '''
    image_count += 1
    next_idx += 1
    if image_count % 100 == 0:
      t1 = time.time()
      print 'Saved image {}: {}'.format(image_count, image_fn)
      print '  {} seconds elapsed'.format(t1-t0)
    # Break if list is empty
    if not locs_list:
      break

  # Save remainder of locations list
  if locs_list:
    pkl.dump(locs_list, open(locs_list_out, 'wb'))
    print 'Saved list of locations: {} locations left'.format(len(locs_list))

  # Print summary when done
  t1 = time.time()
  print 'Saved {} images in {} seconds'.format(image_count, t1-t0)

  return locs_list

##############################################################################################

def determine_next_image_fn(out_dir):
  """
  Determines the next image filename by looking at existing images in a directory. Assumes that images are named by number, in ascending order (i.e., 0.jpg, 1.jpg, etc.).
  :param out_dir: Directory to search within
  :returns: Index of next image
  """
  next_idx = 0
  for image_path in glob.glob(out_dir + '*'):
    image_fn = os.path.basename(image_path)
    image_idx = int(image_fn[:-4])
    if image_idx >= next_idx:
      next_idx = image_idx + 1
  return next_idx

##############################################################################################

def find_locations_within_nl_range(nl_min, nl_max):
  """
  Finds locations where the nightlight value is within the specified range.
  :returns: A list of lat/lon locations [(lat1, lon1), (lat2,lon2)]
  """
  # Load NL values
  nl_tile2 = np.load('/atlas/u/nj/viirs/2015/data/tile2_obs.npy')
  nl_tile5 = np.load('/atlas/u/nj/viirs/2015/data/tile5_obs.npy')
  tile2_tif = '/atlas/u/nj/viirs/2015/1/2/SVDNB_npp_20150101-20150131_75N060W_vcmcfg_v10_c201505111709.avg_rade9.tif'
  tile5_tif = '/atlas/u/nj/viirs/2015/1/5/SVDNB_npp_20150101-20150131_00N060W_vcmcfg_v10_c201505111709.avg_rade9.tif'

  # Find good locations in tiles (row, col)
  within_locs2 = np.array(np.where(np.logical_and((nl_tile2 >= nl_min), (nl_tile2 < nl_max)))).T
  within_locs5 = np.array(np.where(np.logical_and((nl_tile5 >= nl_min), (nl_tile5 < nl_max)))).T

  # Convert to lists of pixel pairs (x, y) or (col, row)
  within_pixel_pairs2 = [(x, y) for y, x in within_locs2]
  within_pixel_pairs5 = [(x, y) for y, x in within_locs5]

  # Convert to lat/lon arrays
  lat_lon_pairs2 = pixel_to_lat_lon(tile2_tif, within_pixel_pairs2)
  lat_lon_pairs5 = pixel_to_lat_lon(tile5_tif, within_pixel_pairs5)
  lats2, lons2 = convert_latlon_pairs_to_arrays(lat_lon_pairs2)
  lats5, lons5 = convert_latlon_pairs_to_arrays(lat_lon_pairs5)
  lats2 -= 15.0 / 3600
  lats5 -= 15.0 / 3600
  lons2 += 15.0 / 3600
  lons5 += 15.0 / 3600

  # Check if lat/lons are in Africa
  within2 = check_batch_within_africa(lats2, lons2)
  within5 = check_batch_within_africa(lats5, lons5)

  # Make a list of lat/lons [(lat1, lon1), (lat2, lon2)]
  within_lats2 = lats2[within2]
  within_lons2 = lons2[within2]
  within_lats5 = lats5[within5]
  within_lons5 = lons5[within5]
  locs_list2 = [(within_lats2[i], within_lons2[i]) for i in xrange(within_lats2.size)]
  locs_list5 = [(within_lats5[i], within_lons5[i]) for i in xrange(within_lats5.size)]
  locs_list = locs_list2 + locs_list5

  return locs_list

##############################################################################################


##############################################################################################


##############################################################################################


##############################################################################################



##############################################################################################



##############################################################################################


##############################################################################################


