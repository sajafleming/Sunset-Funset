from os import listdir, remove
from shutil import copyfile
from osgeo import gdal
import numpy as np

DESTINATION_DIRECTORY = "/Users/Sarah/PROJECT/data/ad_npy/"

# change new img to npy
for img in listdir(DESTINATION_DIRECTORY):
    if ".img" not in img:
        continue
    if img == "n30w091.img":
        continue

    print DESTINATION_DIRECTORY + img

    print DESTINATION_DIRECTORY + img[:-4] + ".npy"

    geo = gdal.Open(DESTINATION_DIRECTORY + img)
    arr = geo.ReadAsArray()

    print arr

    np.save(DESTINATION_DIRECTORY + img[:-4] + ".npy", arr)

    # remove img file
    remove(DESTINATION_DIRECTORY + img)

# geo = gdal.Open("/Users/Sarah/PROJECT/data/aa_npy/n22w090.img")
# arr = geo.ReadAsArray()
# np.save("/Users/Sarah/PROJECT/data/np_arrays/n21w090.npy", arr)

# print arr