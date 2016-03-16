import numpy as np
from osgeo import gdal
from osgeo import osr
import pickle as pkl
from shapely.geometry import Point, Polygon
import time

# The following method translates given latitude/longitude pairs into pixel locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      latLonPairs - The decimal lat/lon pairings to be translated in the form [[lat1,lon1],[lat2,lon2]]
# OUTPUT: The pixel translation of the lat/lon pairings in the form [[x1,y1],[x2,y2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant
def lat_lon_to_pixel(geotifAddr, latLonPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srsLatLong,srs)
	# Go through all the point pairs and translate them to latitude/longitude pairings
	pixelPairs = []
	for point in latLonPairs:
		# Change the point locations into the GeoTransform space
		(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
		# Translate the x and y coordinates into pixel values
		x = (point[1]-gt[0])/gt[1]
		y = (point[0]-gt[3])/gt[5]
		# Add the point to our return array
		pixelPairs.append([int(x),int(y)])
	return pixelPairs

# The following method translates given pixel locations into latitude/longitude locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      pixelPairs - The pixel pairings to be translated in the form [[x1,y1],[x2,y2]]
# OUTPUT: The lat/lon translation of the pixel pairings in the form [[lat1,lon1],[lat2,lon2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant

def pixel_to_lat_lon(geotifAddr,pixelPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srs,srsLatLong)
	# Go through all the point pairs and translate them to pixel pairings
	latLonPairs = []
	for point in pixelPairs:
		# Translate the pixel pairs into untranslated points
		ulon = point[0]*gt[1]+gt[0]
		ulat = point[1]*gt[5]+gt[3]

		# Transform the points to the space
		(lon,lat,holder) = ct.TransformPoint(ulon,ulat)
		# Add the point to our return array
		latLonPairs.append([lat,lon])
 
	return latLonPairs


#The latitude, longitude is confined to (75N/060W) to (65S/060e), which corresponds to tile 2 and 5.
#tile 2 corresponds to (75N/060W) to (00N/060E)
#tile 5 corresponds to (00N/060W) to (65S/060E)
#South and Wast are negative, North and East and positive
#latLongList is a list of (latitude, longitude) tuples

#Returns a list of (latitude, longitude, intensity) tuple
def lat_lon_to_NL(latLongList, tile2dir, tile5dir):

	tile2ds = gdal.Open(tile2dir)
	tile2array = np.array(tile2ds.GetRasterBand(1).ReadAsArray())

	tile5ds = gdal.Open(tile5dir)
	tile5array = np.array(tile5ds.GetRasterBand(1).ReadAsArray())

	#Remove the points not in Africa
	#latLongList_filtered = [x for x in latLongList if IsAfrica(x)]

	latLongList_filtered_tile2 = [x for x in latLongList_filtered if x[0]>=0]
	latLongList_filtered_tile5 = [x for x in latLongList_filtered if x[0]<0]
	
	pixels_tile2 = lat_lon_to_pixel(tile2dir, latLongList_filtered_tile2)
	pixels_tile5 = pixel_to_lat_lon(tile5dir, latLongList_filtered_tile5)

	latLongIntensity_tile2 = []
	latLongIntensity_tile5 = []
	for i in range(len(pixels_tile2)):
		latLongIntensity_tile2.append(latLongList_filtered_tile2[i] + [tile2array[tuple(pixels_tile2[i])]])
	for i in range(len(pixels_tile5)):
		latLongIntensity_tile5.append(latLongList_filtered_tile5[i] + [tile5array[tuple(pixels_tile5[i])]])
		

	#latLongIntensity_tile2 = [pixel+[tile2array[tuple(pixel)]] for pixel in pixels_tile2]
	#latLongIntensity_tile5 = [pixel+[tile5array[tuple(pixel)]] for pixel in pixels_tile5]

	latLongIntensityList = latLongIntensity_tile2 + latLongIntensity_tile5

	return latLongIntensityList

#Returns a list of (latitude, longitude, intensity) tuple
def lat_lon_to_NL_array_input(latLongList, tile2array, tile5array, tile2dir, tile5dir):

	tile2array = tile2array.T
	tile5array = tile5array.T

	#Remove the points not in Africa
	#latLongList_filtered = [x for x in latLongList if IsAfrica(x)]

	latLongList_filtered_tile2 = [x for x in latLongList if x[0]>=0.002]
	latLongList_filtered_tile5 = [x for x in latLongList if x[0]<0]
	
	pixels_tile2 = lat_lon_to_pixel(tile2dir, latLongList_filtered_tile2)
	pixels_tile5 = lat_lon_to_pixel(tile5dir, latLongList_filtered_tile5)

	latLongIntensity_tile2 = []
	latLongIntensity_tile5 = []
	for i in range(len(pixels_tile2)):
		latLongIntensity_tile2.append(latLongList_filtered_tile2[i] + [tile2array[tuple(pixels_tile2[i])]])
	for i in range(len(pixels_tile5)):
		latLongIntensity_tile5.append(latLongList_filtered_tile5[i] + [tile5array[tuple(pixels_tile5[i])]])
		

	#latLongIntensity_tile2 = [pixel+[tile2array[tuple(pixel)]] for pixel in pixels_tile2]
	#latLongIntensity_tile5 = [pixel+[tile5array[tuple(pixel)]] for pixel in pixels_tile5]

	latLongIntensityList = latLongIntensity_tile2 + latLongIntensity_tile5

	return latLongIntensityList

#########################################################################################################

def check_batch_within_africa_jake(lats, lons):
  """
  This function checks arrays of lat/lon locations to see if they are within Africa and returns a list of booleans.
  :param lats: N lats to check
  :param lons: N lons to check
  :return: Length N array of booleans indicating if points are within Africa
  """
  # Load Africa Shapely polygon
  polygon_fn = '../data/shapefiles/africa.pkl'
  africa_polygon = pkl.load(open(polygon_fn, 'rb'))
  t0 = time.time()
  N = lats.size
  within = np.zeros_like(lats)
  for i in xrange(N):
    if lats[i] > 37.352693 or lats[i] < -34.976002 or lons[i]<-18.105469 or lons[i]>52.207031:
      within[i] = 0
    elif -34.976002 < lats[i] < 3.228271 and -18.106549<lons[i]<8.085938:
      within[i] = 0
    elif 7.253496 < lats[i] < 29.592565 and -9.4921881<lons[i]<31.640625:
      within[i] = 1
    elif -21.555284 < lats[i] < 7.253496 and 13.886719<lons[i]<34.804688:
      within[i] = 1
    else:
      point = Point(lons[i], lats[i])
      within[i] = africa_polygon.contains(point)
    if (i + 1) % 10000 == 0:
      print 'Checked {} points: {} seconds'.format(i + 1, time.time() - t0)

  return within.astype(bool)

###########################################################################

def convert_latlon_pairs_to_arrays(lat_lon_pairs):
  lats = []
  lons = []
  for lat_lon in lat_lon_pairs:
    lats.append(lat_lon[0])
    lons.append(lat_lon[1])
  lats = np.array(lats)
  lons = np.array(lons)
  return lats, lons
