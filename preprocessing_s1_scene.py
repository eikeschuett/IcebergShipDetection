# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 10:00:27 2020

@author: eikes
"""

'''
Snappy Code mostly from https://github.com/wajuqi/Sentinel-1-preprocessing-using-Snappy
Subset operator from https://forum.step.esa.int/t/linear-to-from-db-in-python-snappy/15243/4
'''

import datetime
import time
from snappy import ProductIO, jpy, HashMap, GPF
import os
import zipfile
import shutil
import numpy as np
from PIL import Image

def do_apply_orbit_file(source):
    print('\tApply orbit file...')
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    output = GPF.createProduct('Apply-Orbit-File', parameters, source)
    return output

def do_calibration(source, polarization, pols):
    print('\tCalibration...')
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    if polarization == 'DH':
        parameters.put('sourceBands', 'Intensity_HH,Intensity_HV')
    elif polarization == 'DV':
        parameters.put('sourceBands', 'Intensity_VH,Intensity_VV')
    elif polarization == 'SH' or polarization == 'HH':
        parameters.put('sourceBands', 'Intensity_HH')
    elif polarization == 'SV':
        parameters.put('sourceBands', 'Intensity_VV')
    else:
        print("different polarization!")
    parameters.put('selectedPolarisations', pols)
    parameters.put('outputImageScaleInDb', False)
    output = GPF.createProduct("Calibration", parameters, source)
    return output

def do_terrain_correction(source, proj, downsample):
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'GETASSE30')
    # parameters.put('sourceBands', 'Sigma0_HH,Sigma0_HV')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('noDataValueAtSea', False)
    parameters.put('mapProjection', proj)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
    parameters.put('saveProjectedLocalIncidenceAngle', True)
    parameters.put('saveSelectedSourceBand', True)
    # while downsample == 0:                      # downsample: 1 -- need downsample to 40m, 0 -- no need to downsample
    #     parameters.put('pixelSpacingInMeter', 20.0)
    #     break
    output = GPF.createProduct('Terrain-Correction', parameters, source)
    return output

def convert_dB(source):
    print('\tconverting to db…')
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_HH,Sigma0_HV')
    output = GPF.createProduct('LinearToFromdB', parameters, source)
    return output

def do_subset(source, x, y, width, height):
    print('\tSubsetting...')
    parameters = HashMap()
    parameters.put("copyMetadata", True)
    parameters.put('region', "%s,%s,%s,%s" % (x, y, width, height))
    #parameters.put('geoRegion', wkt)
    output = GPF.createProduct('Subset', parameters, source)
    return output

def landseamask(source, vector):
    '''masks area inside a vector of the product'''
    print("landmasking…")
    parameters = HashMap()
    parameters.put('landMask', True)
    parameters.put('useSRTM', False)
    parameters.put('invertGeometry', True)
    parameters.put('geometry', vector)
    parameters.put('shorelineExtension', 50)
    output = GPF.createProduct('Land-Sea-Mask', parameters, source)
    return output

def shp_to_product(product, shp_path, shp_files):
    '''Adds a shapefile to a product'''
    for k in range(len(shp_files)):
        file1 = shp_path + shp_files
        separateShapes = False
        
        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        HashMap = jpy.get_type('java.util.HashMap')
        parameters = HashMap()
        parameters.put('vectorFile', file1)
        parameters.put('separateShapes', separateShapes)
        
        product = GPF.createProduct('Import-Vector', parameters, product)
    return product

def band_to_np(product,band):
    '''Converts a snappy band into a numpy array.'''
    band        = product.getBand(band)
    w           = band.getRasterWidth()
    h           = band.getRasterHeight()
    data        = np.zeros(w * h, dtype=np.float32)
    #Get Data from whole scene and write it into data array
    band.readPixels(0, 0, w, h, data)
    data.shape  = h, w
    return data

###############################################################################
#
# Define important stuff
#

# Define working directory
wdir = "G:/Eigene Dateien/Studium/9. Semester/ML_with_TensorFlow/Project/Data/Testscenes/"
os.chdir(wdir)

# Parameters for subset
# Only process a small subset of the file (otherwise my laptop won't like me anymore)
# May be replaced by geo-coordinates in the future.
x = 11200
y = 8300
width = 1200
height = 1000

# Define path and filename to the land-shapefile which will be used for land masking
# By default, SNAP uses a DEM, but most DEMs don't work in very high latitudes.
# This shapefile is not ideal in terms of spatial resolution but still better than nothing.
# It is available on the drive. 
mask_path    = "Data/Testscenes/GRL_mask/"
mask_file    = "GSL_merge.shp"

# Set proj-string for terrain correction
proj = '''PROJCS["UTM Zone 22 / World Geodetic System 1984", GEOGCS["World Geodetic System 1984", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], \r\n    AXIS["Geodetic latitude", NORTH]], PROJECTION["Transverse_Mercator"], PARAMETER["central_meridian", -51.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996], PARAMETER["false_easting", 500000.0], PARAMETER["false_northing", 0.0], \r\n  UNIT["m", 1.0], AXIS["Easting", EAST], AXIS["Northing", NORTH]]'''

###############################################################################

# Time it
loopstarttime=str(datetime.datetime.now())
print('Start time:', loopstarttime)
start_time = time.time()

###############################################################################

#
# Import scene
# 

# Specify the filename of our scene
file = "S1B_IW_GRDH_1SDH_20200730T100802_20200730T100827_022699_02B151_F93E.zip"
# Unzip scene if required and load it
try:
    product = ProductIO.readProduct(wdir + file[:-4] + ".SAFE")
except RuntimeError:
    print("\nStart unzipping")
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall() # Unzip in working directory
    print("\nDone with unzipping")
    product = ProductIO.readProduct(wdir + file[:-4] + ".SAFE")

## Extract mode, product type, and polarizations from filename
#modestamp = file.split("_")[1]
#productstamp = file.split("_")[2]
polstamp = file.split("_")[3]

polarization = polstamp[2:4]
if polarization == 'DV':
    pols = 'VH,VV'
elif polarization == 'DH':
    pols = 'HH,HV'
elif polarization == 'SH' or polarization == 'HH':
    pols = 'HH'
elif polarization == 'SV':
    pols = 'VV'
else:
    print("Polarization error!")



###############################################################################

#
# Start preprocessing
#

product      = do_apply_orbit_file(product)

product     = do_subset(product, x, y, width, height)

product     = do_calibration(product, polarization, pols)

product     = do_terrain_correction(product, proj, 0)

product     = convert_dB(product)

product     = shp_to_product(product, mask_path, mask_file)

product     = landseamask(product, "GSL_merge")



###############################################################################

#
# Export product
#

# Not exported as .nc file because google colab can't deal with it
# ProductIO.writeProduct(product, wdir + "Output/" + file[:-4] + "_cal_ter_db_UTM_msk_subset", 'netCDF4-BEAM')

# Export images as seperate tif files and combine them in a zip file

bands = ['Sigma0_HH_db', 'Sigma0_HV_db', 'lat', 'lon']

exp_dir = wdir + 'Output/' + file[:-4]

# Create folder for the output, if it doesn't exist
if not os.path.exists(exp_dir):
    os.makedirs(exp_dir)

# Export each band into separate .tifs
for i, band_str in enumerate(bands):
    band = band_to_np(product, band_str)
    Image.fromarray(band).save(exp_dir + "/" + file[:-4] + '_cal_ter_db_UTM_msk_' + band_str + '.tif')

# reloaded = np.array(Image.open(exp_dir + "/" + file[:-4] + '_cal_ter_db_UTM_msk_' + band_str + '.tif'))

# Define filename for the final zip file
# I'm not sure if this is working, but i will check when I'm back in Kiel
output_filename = "./Output/" + file[:-4] + "_output"
# Compress all four tifs in the final zip file
shutil.make_archive(output_filename, 'zip', exp_dir)

# Now upload this .zip-File to our Drive and run Object_Detection.ipynb


# Dont know what this is doing or if it's necessary, but I found it in some examples
product.dispose()
product.closeIO()
print('Done.')
print("--- %s seconds ---" % (time.time() - start_time))




