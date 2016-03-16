from PIL import Image
import urllib2 as urllib
import cStringIO
import os
import random
from optparse import OptionParser
import sys
from data_utils import locsToPixels, pixelsToCoords, get_meanpix, preprocess_image, ThreadPool, point2TilePixel
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc as misc 
from collections import Counter
from osgeo import gdalnumeric, gdal, osr

def download_img(lat, lon, zoom, width, height, i, keys, savedir): 
    try:
        url_satellite = "https://maps.googleapis.com/maps/api/staticmap?center=" + \
            str(lat) + "," + str(lon) + "&zoom=" + str(zoom) + "&size=" + str(width) + "x" + str(height) + \
            "&sensor=false&maptype=satellite&key=" + keys[i%len(keys)]
        f_satellite = cStringIO.StringIO(urllib.urlopen(url_satellite).read())
        img_satellite = Image.open(f_satellite)
        rgb = img_satellite.convert('RGB')
        rgb = rgb.crop((0, 50, width, width + 50))
        filename = "img_" + str(i) + ".jpg"
        print "Saving", filename
        misc.imsave(os.path.join(savedir + str(i / 20000), filename), rgb)
    except:
        pass  

if __name__ == '__main__':
    #Options for running the script
    parser = OptionParser()
    parser.add_option('-f', action="store", dest="locationInputFile", default='DHS_data/dhs_latlon.txt',
                      type="string", help="image to lat-lon file in format [lat] [lon] for each line. Can also be in format [lat] [lon] [label].")
    parser.add_option('-o', action="store", dest="pixelFile", type="string", help="output pixel file. Requires nightlights tif file. One of -o or -l must be used.")
    parser.add_option('--ol', action="store", dest="locFile", type="string", help="output lat-lon file. One of -o or -ol must be used.")
    parser.add_option('-d',action="store", dest="savedir",default="images",type="string",help="save directory. must be made prior to execution")
    parser.add_option('-m',action="store", dest="num_examples",default=25000,type="int",help="total number of examples. can be larger than file size for sampling")
    parser.add_option('-s',action="store", dest="size",default=224,type="int",help="size of one edge of square image")
    parser.add_option('-p',action="store", dest="img_to_pix",type="string",help="img_to_pix file for existing data (not to duplicate samples)")
    parser.add_option('-t',action="store", dest="num_threads", default = 1, type="int", help="number of threads to use")
    parser.add_option('-c', action="store", dest="num_classes", type="int", help="number of classes. Activates class balancing.")
    parser.add_option('-z', action="store", dest="zoom", type = "int", default=16, help="zoom level")
    parser.add_option('-n', action="store", dest="noise", type = "float", default=0.045, help="uniform noise in lat-lon to add")
    parser.add_option('--shuffle', action="store_true", dest="shuffle", default=False, help="Shuffle the order in which the input locations are downloaded from")
    parser.add_option('--tif', action="store", dest="tif", type="string", default= "F182013/F182013.v4c_web.stable_lights.avg_vis.tif", help="tif file if downloading by pixels")
    options, remainder = parser.parse_args()
    savedir = options.savedir
    if not options.locationInputFile:
        print "Need image to lat-lon file in format [lat] [lon] for each line"
        sys.exit(0)
    elif not options.pixelFile and not options.locFile:
        print "Need output file"
        sys.exit(0)
    elif not options.savedir:
        print "Need save directory"
        sys.exit(0)

    existing_pix = []
    if options.img_to_pix:
        #existing samples (don't duplicate these)
        with open(options.img_to_pix, 'r') as f:
            for line in f:
                x = float(line.split()[1])
                y = float(line.split()[2])
                existing_pix.append((x,y))
    existing_pix = Counter(existing_pix)
            
    #API keys used to download images
    keys = ["AIzaSyDzWmvcVKeyoDgyvnLgHpVnCLpypWLrkPY", "AIzaSyBW1imRBOtaa6uwvVRxjlaZ38U0rkjbYzM", "AIzaSyAejgapvGncLMRiMlUoqZ2h6yRF-lwNYMM", "AIzaSyD3f6sozQ3UqlP45Oj_8plnc5KILYC9amU", "AIzaSyAZlsqwvlFBArKqMCbPfE_BMVL_KU6dKSM", "AIzaSyCkRXcAdW-rwh7cpqOOrJBw2agkeftdcDc","AIzaSyCzbSnF_OH2sElz1Mh2xuU0XLaF0oI3DxE"]
    #Thread pool
    pool = ThreadPool(options.num_threads)

    zoom = options.zoom
    i =0 
    latVariance = options.noise #around 5km of latitude variance
    lonVariance = options.noise #much more of an estimate than latitude 
    sample_locs = []
    write_locs = [] #cells
    sample_pixels = []
    output = []
    labels = []
    #nightlights
    if options.pixelFile:
        srcImagePath1 = options.tif
        tile1 = gdalnumeric.LoadFile(srcImagePath1)
        tile2 = None
    
    while(len(sample_locs) < options.num_examples):
        sample_locs_temp = []
        sample_pixels_temp = []
        output_temp = []
        with open(options.locationInputFile, 'r') as infile:
            for line in infile:
                toks = line.strip().split()
                #location to cell location mapping
                if len(toks) == 4:
                    pt = (toks[0], toks[1])
                    write_locs.append((float(toks[2]), float(toks[3])))
                #location to label mapping
                elif len(toks) == 3:
                    pt = (toks[0], toks[1])
                    labels.append(toks[2])     
                else:
                    pt = line.strip().split()
                lat = np.random.uniform(float(pt[0])-latVariance, float(pt[0])+latVariance)
                lon = np.random.uniform(float(pt[1])-lonVariance, float(pt[1])+lonVariance)
                sample_locs_temp.append((lat, lon))
                #write_locs.append((float(pt[0]), float(pt[1]))) 

            #snap to a pixel location
            if options.pixelFile:
                sample_pixels_temp = locsToPixels(srcImagePath1, sample_locs_temp)
                sample_pixels_temp = list(set(sample_pixels_temp)) #discard dups
                print str(len(sample_pixels)) + " non-duplicate pixels"
                sample_pixels_temp = [pix for pix in sample_pixels_temp if not existing_pix.has_key(pix)] #discard existing             
                print str(len(sample_pixels_temp)) + " non-duplicate, non-existing pixels"
                sample_locs_temp = pixelsToCoords(srcImagePath1, sample_pixels_temp)
            
                for idx, point in enumerate(sample_pixels_temp):
                    pixelVal = int(np.round(point2TilePixel(point, tile1, tile2)))
                    if pixelVal < 0:
                        del sample_pixels_temp[idx]
                        del sample_locs_temp[idx]
                        continue
                    output_temp.append(pixelVal)
                output_temp = np.asarray(output_temp)
            
            #balance dataset
            if options.num_classes and options.pixelFile:
                sample_locs_temp = np.asarray(sample_locs_temp)
                class_counts = Counter(output_temp)
                threshold = 2 * np.amin(class_counts.values())
            
                balanced_sample_locs = []
                for i in xrange(options.num_classes):
                    class_idx_mask = (output_temp == i)
                    
                    class_examples = sample_locs_temp[class_idx_mask]
                    
                    m = class_examples.shape[0]
                    if m > threshold:
                        class_examples = class_examples[np.random.choice(range(m), size=threshold, replace=False)]
                    m = class_examples.shape[0]
                    balanced_sample_locs += [(class_examples[j][0], class_examples[j][1]) for j in xrange(m)]
                
                sample_locs_temp = balanced_sample_locs
                sample_pixels_temp = locsToPixels(srcImagePath1, sample_locs_temp)
            
            if options.pixelFile:
                sample_pixels += sample_pixels_temp
                existing_pix.update(sample_pixels_temp)

                output_temp = []
                for idx, point in enumerate(sample_pixels_temp):
                    pixelVal = int(np.round(point2TilePixel(point, tile1, tile2)))
                    output_temp.append(pixelVal)
                output += output_temp
            sample_locs += sample_locs_temp
            print "sampled " + str(len(sample_locs_temp)) + " candidate locations"
    
    #shuffle 
    if options.shuffle:
        np.random.shuffle(sample_locs)
    if options.pixelFile:
        sample_pixels = locsToPixels(srcImagePath1, sample_locs)
        del tile1        
    print str(len(sample_locs)) + " locations sampled"
    
    write_lines = []
    write_lines_locs = []
    for idx, loc in enumerate(sample_locs):
        if i >= options.num_examples:
            break
        lat, lon = loc
         #want x by x but getting a bit larger picture
        width = options.size
        height = options.size + 100
        if height > 640: 
            height = 640        
        pool.add_task(download_img, lat, lon, zoom, width, height, i, keys, savedir)
                    
        filename = "img_" + str(i) + ".jpg"
        if i % 20000 == 0:
            os.makedirs(savedir + str(i / 20000))
                 
        if options.pixelFile:
            pixel = sample_pixels[idx]
            x,y = pixel
            write_line = os.path.join(savedir + str(i / 20000), filename) + " " + str(x) + " " + str(y)  
            write_lines.append(write_line)
        elif options.locFile:
            if len(write_locs) > 0:
                write_lines_locs.append(os.path.join(savedir + str(i / 20000), filename) + " " + str(lat) + " " + str(lon) + " " + str(write_locs[idx][0]) + " " + str(write_locs[idx][1]))
            else:
                write_lines_locs.append("%s %f %f\n" % (os.path.join(savedir + str(i / 20000), filename), lat, lon)) 
        i+=1
    pool.wait_completion()
    meanpix = np.zeros(3)
    num_imgs = 0
    if options.pixelFile:
        with open(options.pixelFile, 'w') as f:
            for line in write_lines: 
                img_path = line.split()[0]
                
                file_size = os.stat(img_path).st_size
                if file_size < 10000:
                    os.remove(img_path)
                    continue
 
                try:
                    img = misc.imread(img_path)
                except:
                    continue
                curr_meanpix = get_meanpix(np.asarray(img))
                #filter out white and black images (image not found, bad areas to sample from)`
                if (np.sum(curr_meanpix) / 3) > 225 or (np.sum(curr_meanpix) / 3) < 30:
                    continue
                meanpix += curr_meanpix
                f.write(line + '\n')
                num_imgs += 1
    if options.locFile: 
         with open(options.locFile, 'w') as f:
            for line in write_lines_locs: 
                img_path = line.split()[0]
                print img_path
                try:
                    file_size = os.stat(img_path).st_size
                    if file_size < 10000:
                        os.remove(img_path)
                        continue

                    img = misc.imread(img_path)
                except:
                    continue
                curr_meanpix = get_meanpix(np.asarray(img))
                #filter out white and black images (image not found, bad areas to sample from)`
                if (np.sum(curr_meanpix) / 3) > 225 or (np.sum(curr_meanpix) / 3) < 30:
                    continue
                meanpix += curr_meanpix
                f.write(line + '\n')
                num_imgs += 1
    meanpix /= float(num_imgs)
    print "MEAN PIXEL RGB: ", meanpix
