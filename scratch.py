# Reading img files

from osgeo import gdal

def read_img_file(filename):
    """Read a IMG formatted file and return a numpy array with GDAL."""

    geo = gdal.Open(filename)
    arr = geo.ReadAsArray()

    return arr

# more functions

def find_local_max(array):
    """Find local maximums of 2D array and return indexes."""
    # use algorithm below
    # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax
    pass


def check_obstructions_west(index):
    """Check that there are no obstructions to the west given an index"""
    pass
    