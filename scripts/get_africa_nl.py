import numpy as np
import time
from PIL import Image
from neal_utils import *

##############################################################################################

# NL tile locations
tile2_addr = '/atlas/u/nj/viirs/2015/12/2/SVDNB_npp_20151201-20151231_75N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'
tile5_addr = '/atlas/u/nj/viirs/2015/12/5/SVDNB_npp_20151201-20151231_00N060W_vcmcfg_v10_c201601251413.avg_rade9.tif'

# Average NL observations files
tile2_obs_fn = '/atlas/u/nj/viirs/2015/data/tile2_obs.npy'
tile5_obs_fn = '/atlas/u/nj/viirs/2015/data/tile5_obs.npy'

# Output file names
tile2_nl_fn = '/atlas/u/nj/viirs/2015/data/africa_nl/tile2_africa_nl.npy'
tile5_nl_fn = '/atlas/u/nj/viirs/2015/data/africa_nl/tile5_africa_nl.npy'

##############################################################################################

if False:
  # Process tile 2

  geotif = Image.open(tile2_addr)
  tile_obs = np.load(tile2_obs_fn)

  # Pixels to search
  lowest_x = 4800
  highest_x = 27120
  lowest_y = 8880
  highest_y = 18000

  # Store NL values within Africa in huge list
  tile2_nl_values = []

  # Process values in batches
  x_grid = range(lowest_x, highest_x, 10000) + [highest_x]
  y_grid = range(lowest_y, highest_y, 100) + [highest_y]
  # Create batches
  t0 = time.time()
  batch_num = 0
  for x_idx in xrange(len(x_grid) - 1):
    for y_idx in xrange(len(y_grid) - 1):
      low_x, high_x = x_grid[x_idx], x_grid[x_idx + 1]
      low_y, high_y = y_grid[y_idx], y_grid[y_idx + 1]
      batch_num += 1
      print 'Processing batch {}: {} seconds elapsed'.format(batch_num, time.time() - t0)

      # Produce list of pixel pairs
      pixel_pairs = make_pixel_pairs(low_x, high_x, low_y, high_y)

      # Convert pixel pairs to lat/lon pairs
      lat_lon_pairs = pixel_to_lat_lon(tile2_addr, pixel_pairs)

      # Check whether lat/lon pairs are in Africa
      lats, lons = convert_latlon_pairs_to_arrays(lat_lon_pairs)
      within = check_batch_within_africa(lats, lons)

      # Get NL values for pixels in Africa
      pixel_pairs_in_africa = np.array(pixel_pairs)
      pixel_pairs_in_africa = pixel_pairs_in_africa[within]
      nl_values = []
      for i in xrange(pixel_pairs_in_africa.shape[0]):
        nl_values.append(tile_obs[pixel_pairs_in_africa[i,1], pixel_pairs_in_africa[i,0]])

      # Add new NL values to total NL values in Africa
      tile2_nl_values += nl_values
      print 'Finished batch {}: {} seconds elapsed'.format(batch_num, time.time() - t0)

  # Save NL values within Africa for tile 2
  tile2_nl_array = np.array(tile2_nl_values)
  np.save(tile2_nl_fn, tile2_nl_array)

##############################################################################################

if True:
  # Process tile 5

  geotif = Image.open(tile5_addr)
  tile_obs = np.load(tile5_obs_fn)

  # Pixels to search
  lowest_x = 16320
  highest_x = 24960
  lowest_y = 0
  highest_y = 8640

  # Store NL values within Africa in huge list
  tile5_nl_values = []

  # Process values in batches
  x_grid = range(lowest_x, highest_x, 10000) + [highest_x]
  y_grid = range(lowest_y, highest_y, 100) + [highest_y]
  # Create batches
  t0 = time.time()
  batch_num = 0
  for x_idx in xrange(len(x_grid) - 1):
    for y_idx in xrange(len(y_grid) - 1):
      low_x, high_x = x_grid[x_idx], x_grid[x_idx + 1]
      low_y, high_y = y_grid[y_idx], y_grid[y_idx + 1]
      batch_num += 1
      print 'Processing batch {}: {} seconds elapsed'.format(batch_num, time.time() - t0)

      # Produce list of pixel pairs
      pixel_pairs = make_pixel_pairs(low_x, high_x, low_y, high_y)

      # Convert pixel pairs to lat/lon pairs
      lat_lon_pairs = pixel_to_lat_lon(tile5_addr, pixel_pairs)

      # Check whether lat/lon pairs are in Africa
      lats, lons = convert_latlon_pairs_to_arrays(lat_lon_pairs)
      within = check_batch_within_africa(lats, lons)

      # Get NL values for pixels in Africa
      pixel_pairs_in_africa = np.array(pixel_pairs)
      pixel_pairs_in_africa = pixel_pairs_in_africa[within]
      nl_values = []
      for i in xrange(pixel_pairs_in_africa.shape[0]):
        nl_values.append(tile_obs[pixel_pairs_in_africa[i,1], pixel_pairs_in_africa[i,0]])

      # Add new NL values to total NL values in Africa
      tile5_nl_values += nl_values
      print 'Finished batch {}: {} seconds elapsed'.format(batch_num, time.time() - t0)

  # Save NL values within Africa for tile 5
  tile5_nl_array = np.array(tile5_nl_values)
  np.save(tile5_nl_fn, tile5_nl_array)

