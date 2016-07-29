import numpy as np
from osgeo import gdal

geo = gdal.Open("/Users/Sarah/PROJECT/data/ai_img/n21w090.img")
arr = geo.ReadAsArray()

np.save("/Users/Sarah/PROJECT/data/np_arrays/n21w090.npy", arr)