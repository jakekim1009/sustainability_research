import numpy as np
from osgeo import gdal
from latlong_to_pixelcoord import latLonToPixel
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm


def IsAfrica(latLong):
	return 1

def LatLongToLightIntensity(latLongList, tile2dir, tile5dir):
#The latitude, longitude is confined to (75N/060W) to (65S/060e), which corresponds to tile 2 and 5.
#tile 2 corresponds to (75N/060W) to (00N/060E)
#tile 5 corresponds to (00N/060W) to (65S/060E)
#South and Wast are negative, North and East and positive
#latLongList is a list of (latitude, longitude) tuples

#Returns a list of (latitude, longitude, intensity) tuple

	tile2ds = gdal.Open(tile2dir)
	tile2array = np.array(tile2ds.GetRasterBand(1).ReadAsArray())

	tile5ds = gdal.Open(tile5dir)
	tile5array = np.array(tile5ds.GetRasterBand(1).ReadAsArray())


	#latLongList_filtered = [x for x in latLongList if IsAfrica(x)]

	latLongList_filtered_tile2 = [x for x in latLongList_filtered if x[0]>=0]
	latLongList_filtered_tile5 = [x for x in latLongList_filtered if x[0]<0]
	
	pixels_tile2 = latLonToPixel(tile2dir, latLongList_filtered_tile2)
	pixels_tile5 = latLonToPixel(tile5dir, latLongList_filtered_tile5)

	#print pixels_tile2
	#print pixels_tile5
	#print tile2array.shape
	#print tile5array.shape

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



tile2dir = './SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'
tile5dir = './SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'


n = 100 
x = np.linspace(2., 8., n) 
y = np.linspace(0., 12., n) 


latLongList = []
for i in range(n):
	for j in range(n):
		 latLongList.append([x[i], y[j]])
data = np.array(LatLongToLightIntensity(latLongList, tile2dir, tile5dir))

x = data[:,0]
y = data[:,1]
z = data[:,2]

z = np.maximum(z, 100)
z = np.minimum(z, 1e-5)
z = np.log(z)

plt.scatter(x,y,c=z, cmap='gray');
plt.show()

#X, Y = np.meshgrid(x, y)
#z = z.reshape(n,n)
#plt.pcolormesh(Y, X, z, cmap = cm.gray) 
#plt.show()


#numPoints = 50
#latLongList = []
#for i in range(numPoints):
#	for j in range(numPoints):
#		latLongList.append([2 + 6 * float(i) / numPoints, 12 * float(j) / numPoints])
#latLongList = [[8.0, 0.0],[2.0, 12.0]]
#data = np.array(LatLongToLightIntensity(latLongList, tile2dir, tile5dir))

#How to draw this?
#Longitude comes first
#y = data[:,0]
#x = data[:,1]
#z = data[:,2]

#plt.scatter(x,y,c=z, marker = 'o');
#plt.show()