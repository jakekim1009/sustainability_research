import numpy as np
from osgeo import gdal
from latlong_to_pixelcoord import latLonToPixel
from latlong_to_pixelcoord import returnOnlyAfrica
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

def IsAfrica(latLong):
	return 1

def DrawHistogram():
#The latitude, longitude is confined to (75N/060W) to (65S/060e), which corresponds to tile 2 and 5.
#tile 2 corresponds to (75N/060W) to (00N/060E)
#tile 5 corresponds to (00N/060W) to (65S/060E)
#South and Wast are negative, North and East and positive
#latLongList is a list of (latitude, longitude) tuples

#Removes the locations that are not in Africa, and draws histogram of the African region intensities.

	tile2dir = './SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'
	tile5dir = './SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'
	tile2ds = gdal.Open(tile2dir)
	tile2array = np.array(tile2ds.GetRasterBand(1).ReadAsArray())
	tile5ds = gdal.Open(tile5dir)
	tile5array = np.array(tile5ds.GetRasterBand(1).ReadAsArray())

	#limiting it to a small part
	#tile2array = tile2array[0:10, 0:10]
	#tile5array = tile5array[0:10, 0:10]

	tile2PixelPairs = []
	for i in range(tile2array.shape[0]):
		for j in range(tile2array.shape[1]):
			tile2PixelPairs.append([i,j])
	tile5PixelPairs = []
	for i in range(tile5array.shape[0]):
		for j in range(tile5array.shape[1]):
			tile5PixelPairs.append([i,j])

	tile2PixelPairs_Africa = returnOnlyAfrica(tile2dir, tile2PixelPairs)
	tile5PixelPairs_Africa = returnOnlyAfrica(tile5dir, tile5PixelPairs)
	
	tile2Intensities = []
	tile5Intensities = []
	for point in tile2PixelPairs_Africa:
		tile2Intensities.append(tile2array[tuple(point)])
	for point in tile5PixelPairs_Africa:
		tile5Intensities.append(tile5array[tuple(point)])

	intensities = np.array(tile2Intensities + tile5Intensities)

	intensities = np.maximum(intensities, 100)
	intensities = np.minimum(intensities, 1e-5)
	intensities = np.log(intensities)

	hist, bins = np.histogram(intensities, bins=10)
	width = 0.7 * (bins[1] - bins[0])
	center = (bins[:-1] + bins[1:]) / 2
	plt.bar(center, hist, align='center', width=width)
	plt.savefig('AfricaIntensityHistogram.jpg')

DrawHistogram()

