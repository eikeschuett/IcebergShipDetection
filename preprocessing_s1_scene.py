# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 10:00:27 2020

@author: eikes
"""

'''
This code prepares a Sentinel-1 IW HH+HV scene for the iceberg-ship-detection
model (see https://github.com/eikeschuett/IcebergShipDetection).

This code uses the Sentinel Application Platform (SNAP) Python API for the 
preprocessing of the satellite image. It is therefore required to run this code
in an environment which has SNAP installed and snappy properly set up. More 
information on this are available here: 
https://towardsdatascience.com/getting-started-with-snap-toolbox-in-python-89e33594fa04

Sentinel-1 images can be downloaded for free from the Copernicus Open Access 
Hub (https://scihub.copernicus.eu/dhus/#/home). Make sure to use 'GRD' as your
Product Type, 'HH+HV' as Polarisation and IW as Sensor Mode. The model has been
trained with this kind of data. The model may also work with VV+VH polarisation
or different acquisition modes, but this has not been tested.

This code will work with the original downloaded satellite scenes (.zip) and 
unzip it on the fly.

The preprocessing contains the following steps: Apply an orbit file, take a subset
of the satellite scene, do calibration, convert to dBand apply a land-sea-mask, 
so that land areas are flagged. This step requires a shapefile of the water area 
(e.g.  from https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-ocean/).

Output of this preprocessing is a zip-file which contains 5 tif-files:
    - Sigma0_HH_db
    - Sigma0_HV_db
    - local inclination angle
    - Latitude
    - Longitude
    
This zip-file may then be uploaded into a drive and can be used as input for the
iceberg-ship-detection model (Object_Detection.ipynb in the GitHub repository).

This data format is not ideal, but unfortunately Google Colab can handle more
common types like netCDF-Files or GeoTIFFs.

The first part of the code defines of the working directory, the file that is
to be processed and other hyperparameters. Define these according to your local
environment and preferences.

Snappy Code customized from https://github.com/wajuqi/Sentinel-1-preprocessing-using-Snappy
Subset operator from https://forum.step.esa.int/t/linear-to-from-db-in-python-snappy/15243/4
'''


###############################################################################
#
# Define directories, the scene and other important stuff
#
###############################################################################

# Define working directory
wdir = "H:/Eigene Dateien/Studium/9. Semester/ML_with_TensorFlow/Project/Data/Testscenes/"


# Specify the filename of our scene
file = "S1B_IW_GRDH_1SDH_20200730T100802_20200730T100827_022699_02B151_F93E.zip"

# Parameters for subset
# May be replaced by geo-coordinates in the future.
x = 11200 # 11830
y = 8300 # 12563
width = 1200 # 1051
height = 1000 # 1051

# Define path and filename to the water-shapefile which will be used for land masking.
# By default, SNAP uses a DEM, but most DEMs don't work in very high latitudes.
# This shapefile is not ideal in terms of spatial resolution and accuracy but still better than nothing.
# It is available at https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-ocean/. 
mask_path    = wdir + "ne_10m_ocean/"
mask_file    = "ne_10m_ocean.shp"

# Set proj-string for terrain correction. The scene will be reprojected to this CRS.
# Only required if terrain correction is carried out. Currently not needed
# For Disko Bay Area (UTM Zone 22):
# proj = '''PROJCS["UTM Zone 22 / World Geodetic System 1984", GEOGCS["World Geodetic System 1984", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], \r\n    AXIS["Geodetic latitude", NORTH]], PROJECTION["Transverse_Mercator"], PARAMETER["central_meridian", -51.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996], PARAMETER["false_easting", 500000.0], PARAMETER["false_northing", 0.0], \r\n  UNIT["m", 1.0], AXIS["Easting", EAST], AXIS["Northing", NORTH]]'''
# String for Svalbard Area (UTM Zone 33):
# proj = '''PROJCS["UTM Zone 33 / World Geodetic System 1984" ,GEOGCS["World Geodetic System 1984", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Geodetic longitude", EAST], \r\n    AXIS["Geodetic latitude", NORTH]], PROJECTION["Transverse_Mercator"], PARAMETER["central_meridian", 15.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["scale_factor", 0.9996], PARAMETER["false_easting", 500000.0], PARAMETER["false_northing", 0.0], \r\n  UNIT["m", 1.0], AXIS["Easting", EAST], AXIS["Northing", NORTH]]'''			    


# Define folder for output relative to working directory
exp_dir = wdir + 'Output/' + file[:-4]


###############################################################################
#
# Import required libraries
#
###############################################################################

import datetime
import time
from snappy import ProductIO, jpy, HashMap, GPF
import os
import zipfile
import shutil
import numpy as np
from PIL import Image
import tempfile

###############################################################################
#
# Define functions
#
###############################################################################

def apply_orbit_file(source):
    print('\tApply orbit file...')
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    output = GPF.createProduct('Apply-Orbit-File', parameters, source)
    return output

def calibration(source, polarization, pols):
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

def terrain_correction(source, proj, downsample):
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'GETASSE30')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('noDataValueAtSea', False)
    parameters.put('mapProjection', proj)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
    parameters.put('saveProjectedLocalIncidenceAngle', True)
    parameters.put('saveSelectedSourceBand', True)
    output = GPF.createProduct('Terrain-Correction', parameters, source)
    return output

def convert_dB(source):
    print('\tconverting to db…')
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_HH,Sigma0_HV')
    output = GPF.createProduct('LinearToFromdB', parameters, source)
    return output

def subset(source, x, y, width, height):
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
    #parameters.put('sourceBands', 'Sigma0_HH_db')
    parameters.put('landMask', True)
    parameters.put('useSRTM', False)
    parameters.put('invertGeometry', False)
    parameters.put('geometry', vector)
    parameters.put('shorelineExtension', 100)
    output = GPF.createProduct('Land-Sea-Mask', parameters, source)
    return output

def shp_to_product(product, shp_path, shp_files):
    '''Adds a shapefile to a product'''
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

def TpGrid_to_np(product,TpGrid):
    '''Converts a snappy band into a numpy array.'''
    TpGrid      = product.getTiePointGrid(TpGrid)
    w           = TpGrid.getRasterWidth()
    h           = TpGrid.getRasterHeight()
    data        = np.zeros(w * h, dtype=np.float32)
    #Get Data from whole scene and write it into data array
    TpGrid.readPixels(0, 0, w, h, data)
    data.shape  = h, w
    return data

def get_tempfile_name(some_id):
    return os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + "_" + some_id)



# Set working directory
os.chdir(wdir)

###############################################################################

# Time it
loopstarttime=str(datetime.datetime.now())
print('Start time:', loopstarttime)
start_time = time.time()

###############################################################################
# Create folder for the output, if it doesn't exist
if not os.path.exists(exp_dir):
    os.makedirs(exp_dir)

###############################################################################
#
# Import scene
# 
###############################################################################

# Unzip scene if required and load it
try:
    product = ProductIO.readProduct(wdir + file[:-4] + ".SAFE")
except RuntimeError:
    print("\nStart unzipping")
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall() # Unzip in working directory
    print("\nDone with unzipping")
    product = ProductIO.readProduct(wdir + file[:-4] + ".SAFE")

###############################################################################
#
# Extract mode, product type, and polarizations from filename
#
###############################################################################
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
###############################################################################

product     = apply_orbit_file(product)

product     = subset(product, x, y, width, height)

# Save the local incidence angle because it will be lost in the next processing steps
inc_angle  = TpGrid_to_np(product,"incident_angle")
Image.fromarray(inc_angle).save(exp_dir + "/" + file[:-4] + 'cal_ter_db_UTM_msk_projectedLocalIncidenceAngle_test.tif')

product     = calibration(product, polarization, pols)

#p2     = terrain_correction(product, proj, 0)

product     = convert_dB(product)

product     = shp_to_product(product, mask_path, mask_file)

product     = landseamask(product, mask_file[:-4])


###############################################################################
#
# Save the preprocessed product temporarily and reload it.
# This is necessary, because the product contains no lat/lon-bands in snappy.
# You can check all bands that the product contains with
# print(list(product.getBandNames()))
# However, when the product is exported, lat/lon bands are created and still
# exist when the product is imported back into snappy.
# This is no nice solution, but I havn't found a better workaround.
#
###############################################################################

temp_fname = get_tempfile_name('a')
ProductIO.writeProduct(product, temp_fname, 'netCDF4-BEAM')

# Then reopen temporary file
product = ProductIO.readProduct(temp_fname + ".nc")
#print(list(product.getBandNames()))


###############################################################################
#
# Export products as tifs and compress them in a final .zip file
# Not exported as .nc file or GeoTIFs because google colab handle them
#
###############################################################################


bands = ['Sigma0_HH_db', 'Sigma0_HV_db', 'lat', 'lon']

# Export each band into separate .tifs
for i, band_str in enumerate(bands):
    band = band_to_np(product, band_str)
    Image.fromarray(band).save(exp_dir + "/" + file[:-4] + '_cal_ter_db_UTM_msk_' + band_str + '.tif')


# Define filename for the final zip file
output_filename = "./Output/" + file[:-4] + "_output"
# Compress all four tifs in the final zip file
shutil.make_archive(output_filename, 'zip', exp_dir)
# Now upload this .zip-File to our Drive and run Object_Detection.ipynb

# Delete folder with TIFs and only keep the .zip-File
shutil.rmtree(exp_dir)

product.dispose()
product.closeIO()
print('Done. Upload ./Output/' + file[:-4] + "_output.zip into the Drive and run the object detection code.")
print("--- %s seconds ---" % (time.time() - start_time))




