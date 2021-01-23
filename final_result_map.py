# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:10:04 2021

@author: eikes
"""


###############################################################################
#
# Define directories, the inout file and other important stuff
#
###############################################################################

# Specify your working directory
wdir = "H:/Eigene Dateien/Studium/9. Semester/ML_with_TensorFlow/Project/Data/Testscenes/Output/"

# Specify your input filename (a CSC-File from Object_Detection.ipynb)
# This file must be in the working directory
file = "geo_output_S1A_IW_GRDH_1SDH_20210115T100027_20210115T100052_036147_043CF4_049C.csv"

# Specify the extent of the map
lat_min = 69
lat_max = 69.3
lon_min = -54.4
lon_max = -53 

# Specify the desired zoom level of the background map 
# (smaller numbers for smaller scales and vice versa)
zoom = 10



###############################################################################
#
# Import required libraries
#
###############################################################################

import pandas as pd
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np



###############################################################################
#
# Define a function to plot a scale bar into the map
#
###############################################################################

def scale_bar(ax, length=None, location=(0.5, 0.05), linewidth=8):
    """
    ax is the axes to draw the scalebar on.
    length is the length of the scalebar in km.
    location is center of the scalebar in axis coordinates.
    (ie. 0.5 is the middle of the plot)
    linewidth is the thickness of the scalebar.
    from https://stackoverflow.com/questions/32333870/how-can-i-show-a-km-ruler-on-a-cartopy-matplotlib-plot
    """
    #Get the limits of the axis in lat long
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    #Make tmc horizontally centred on the middle of the map,
    #vertically at scale bar location
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]
    tmc = ccrs.TransverseMercator(sbllx, sblly, approx=True)
    #Get the extent of the plotted area in coordinates in metres
    x0, x1, y0, y1 = ax.get_extent(tmc)
    #Turn the specified scalebar location into coordinates in metres
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    #Calculate a scale bar length if none has been given
    #(Theres probably a more pythonic way of rounding the number but this works)
    if not length: 
        length = (x1 - x0) / 5000 #in km
        ndim = int(np.floor(np.log10(length))) #number of digits in number
        length = round(length, -ndim) #round to 1sf
        #Returns numbers starting with the list
        def scale_number(x):
            if str(x)[0] in ['1', '2', '5']: return int(x)        
            else: return scale_number(x - 10 ** ndim)
        length = scale_number(length) 

    #Generate the x coordinate for the ends of the scalebar
    bar_xs = [sbx - length * 500, sbx + length * 500]
    #Plot the scalebar
    ax.plot(bar_xs, [sby, sby], transform=tmc, color='k', linewidth=linewidth, zorder=10)
    ax.plot(bar_xs, [sby, sby], transform=tmc, color='w', linewidth=linewidth+3, zorder=5)
    #Plot the scalebar label
    ax.text(sbx, sby+150, str(length) + ' km', color='w', transform=tmc,
            horizontalalignment='center', verticalalignment='bottom', fontsize=20)



###############################################################################
#
# Set working directory and prepare data
#
###############################################################################

os.chdir(wdir)

# Import data
data = pd.read_csv(file, sep="\t")
# Create a separate dataframe for each object class
icebergs = data[data.object=='iceberg']
ships = data[data.object=='ship']
ufo = data[data.object=='UFO']

# Define the background map (from  Windows or Google)
request = cimgt.QuadtreeTiles()
#request = cimgt.GoogleTiles(style="satellite")

# Create polygon of the extent of the subset
poly_corners = np.array([data.lon[0:4], data.lat[0:4]]).T



###############################################################################
#
# Define the figure
#
###############################################################################

fig = plt.figure(figsize=(10, 10))
# Create axis and assign it the coordinate reference system of the background map
ax = plt.axes(projection=request.crs)

# Plot ships, icebergs and ufos in different colours
if len(ships)>0:
    ax.plot(ships.lon, ships.lat, 'ro', markersize=5, transform=ccrs.PlateCarree(), label="Ship")
if len(icebergs)>0:
    ax.plot(icebergs.lon, icebergs.lat, 'bo', markersize=5, transform=ccrs.PlateCarree(), label="Iceberg")
if len(ufo)>0:
    ax.plot(ufo.lon, ufo.lat, 'yo', markersize=5, transform=ccrs.PlateCarree(), label="UFO")

# Create a polygon of the satellite image subset and plot its outline
poly = mpatches.Polygon(poly_corners, closed=True, ec='w', fill=False, lw=1, fc=None, transform=ccrs.PlateCarree())
ax.add_patch(poly)

# Add the background map with the specified zoom level
ax.add_image(request, zoom)

# Add gridlines and labels
gl = ax.gridlines(draw_labels=True, alpha=0.2)
gl.top_labels = gl.right_labels = False

# Create Proxy artists for legend of lakes 
v0 = mlines.Line2D([], [], color='None', mfc='b', mec='b', marker='o', label="Iceberg")
v1 = mlines.Line2D([], [], color='None', mfc='r', mec='r', marker='o', label="Ship")
v2 = mlines.Line2D([], [], color='None', mfc='y', mec='y', marker='o', label="UFO")
v3 = mpatches.Patch(edgecolor='w', facecolor='None', lw=2, label='satellite image subset')

# Create legend from proxies
legend = ax.legend(loc="upper right", ncol=1,
          handles=[v0, v1,v2, v3], fontsize=10, facecolor="darkgray")

# Set the extent of the map
ax.set_extent([lon_min, lon_max, lat_min, lat_max])

# Create a nice title for the map
ax.set_title("Iceberg-Ship-Classification at " + file[28:32] + "-" + 
             file[32:34] + "-" + 
             file[34:36] + " " +
             file[37:39] + ":" + file[39:41] + " UTC\n" +
             file[11:-4])

# Add the scale bar at the lower left of the map
scale_bar(ax, location=(0.15, 0.05))


###############################################################################
#
# Save the map into the working directory
#
###############################################################################

out_file    = 'Map_Iceberg_Ship_Classifier_' + file[11:41] + '.png'
plt.savefig(out_file, dpi=150, bbox_inches='tight', pad_inches=0)


