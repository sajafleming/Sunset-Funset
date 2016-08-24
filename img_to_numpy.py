"""Renaming img files and converting to npy"""

from os import listdir, remove
from shutil import copyfile, move, rmtree
from osgeo import gdal
import numpy as np


# edit directory per file split
ORIGIN_DIRECTORY = "/Users/Sarah/PROJECT/data/ai/"
DESTINATION_DIRECTORY = "/Users/Sarah/PROJECT/data/ai_npy/"

for dir_name in listdir(ORIGIN_DIRECTORY):
    if "USGS" not in dir_name:
        continue
    for name in listdir(ORIGIN_DIRECTORY + dir_name):
        if not name.endswith(".img"):
            continue

        if len(name) == 16:
            new_name = name[3:-6]
        elif len(name) == 26:
            new_name = name[11:-8]

        # rename file (move)
        move(ORIGIN_DIRECTORY + dir_name + "/" + name,
            DESTINATION_DIRECTORY + new_name + ".img")

        # delete folder
        rmtree(ORIGIN_DIRECTORY + dir_name)



# change new img to npy
for img in listdir(DESTINATION_DIRECTORY):
    # skip weird .ds_store files
    if ".img" not in img:
        continue

    # open file and read as array
    geo = gdal.Open(DESTINATION_DIRECTORY + img)
    arr = geo.ReadAsArray()

    # same npy array
    np.save(DESTINATION_DIRECTORY + img[:-4] + ".npy", arr)

    # remove img file
    remove(DESTINATION_DIRECTORY + img)



# two formats
# imgn34w089_1.img -> len 16
# USGS_NED_1_n31w084_IMG.img -> len 26