# functions that know how to function

from osgeo import gdal
from math import ceil
import scipy
import scipy.signal
import numpy as np
import os
from scipy.ndimage.filters import generic_filter as gf
from flask_sqlalchemy import SQLAlchemy



def find_tile_name(latlong):
    """Find the filename that includes the latlong given. Return latlong and
    the n and w integer values."""
    # take the ceiling of the tuple (all files are named according to NW coordinate)

    n = ceil(latlong[0])
    w = ceil(latlong[1])

    # create file name string
    filename = "n%sw%s.img" % (n, w)

    return filename, n, w # don't need filename but may need later


def generate_filenames_list(n, w):
    """Generate filename given north and west coordinates"""

    n = int(n)
    w = int(w)

    # create list of filenames of the surrounding img files

    # RE NAME WITH LOCATIONS

    filenames = ({ 0: "n%sw%s.img" % (n + 1, w - 1),
                   1: "n%sw%s.img" % (n + 1, w),
                   2: "n%sw%s.img" % (n + 1, w + 1),
                   3: "n%sw%s.img" % (n, w -1),
                   4: "n%sw%s.img" % (n, w),
                   5: "n%sw%s.img" % (n, w + 1),
                   6: "n%sw%s.img" % (n - 1, w - 1),
                   7: "n%sw%s.img" % (n - 1, w),
                   8: "n%sw%s.img" % (n - 1, w + 1)})
    # print filenames
    return filenames


def read_img_file(filename):
    """Read img file as numpy array given a filename"""

    geo = gdal.Open(filename)
    # print geo
    # print type(geo)
    arr = geo.ReadAsArray()

    # print arr
    return arr

# def read_surrounding_tiles(latlong):
#     """Create array from img files. Return a numpy array with GDAL.
#     return arrays surrounding as well."""

def create_master_array(latlong):
    """Create one giant array surrounding the user's inputted latlong

    [0][1][2]
    [3][4][5]
    [6][7][8] Format of big array using indices from filelist dictionary
    """

    center_tile, n, w = find_tile_name(latlong)

    # filenames_list = generate_filenames_list(n, w)
    # print filenames_list

    filename_dict = generate_filenames_list(n, w)

    for file_key in filename_dict:
        # create file path for particular filename
        filename = "/Users/Sarah/PROJECT/imgfiles/" + filename_dict[file_key]
        if os.path.isfile(filename):
            # print filename
            filename_dict[file_key] = read_img_file(filename) # MAKE NEW DICT FOR THIS - NO LONGER FILENAMES
        else:
            # make array of all zeros if file doesn't exist
            # using an array from a file I know exists to know what dimensions are
            look_alike = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img")

            #use this array to make a look alike - will have same dimensions with all zeros
            filename_dict[file_key] = np.zeros_like(look_alike)

    master_array = (scipy.vstack((
                           scipy.hstack((filename_dict[0], filename_dict[1], filename_dict[2])),
                           scipy.hstack((filename_dict[3], filename_dict[4], filename_dict[5])),
                           scipy.hstack((filename_dict[6], filename_dict[7], filename_dict[8]))
                          )))
    return master_array


# create_master_array((32.0005,116.9999))
# /Users/Sarah/PROJECT/imgfiles/n33w117.img

def set_radius(latlong, master_array):
    """Narrow down the master array to approximately a 20 mile radius (3612 entries)

    center: (a,b) """

    master_array = create_master_array((32.0005,116.9999))

    a = ceil(latlong[0])
    b = ceil(latlong[1])

    # VisibleDeprecationWarning: boolean index did not match indexed array along 
    # dimension 0; dimension is 10836 but corresponding boolean dimension is 10835
    n = 10836
    r = 3612

    # for testing

    # a = 3
    # b = 3
    # n = 10
    # r = 3

    # hey = np.ones((10,10))
    # hey[mask] = 0
    # return hey

    y,x = np.ogrid[-a:n-a, -b:n-b]
    mask = x**2 + y**2 > r**2

    master_array[mask] = 0

    print master_array
    return master_array

# set_radius((32.0005,116.9999))

def find_local_maxima(latlong):
    """Find local maximums of 2D array and return indexes."""
    # use algorithm below
    # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax
    master_array = create_master_array(latlong)
    radius_array = set_radius(latlong, master_array)

    highest = scipy.signal.argrelmax(radius_array)

    print "AHHH"
    print highest
    return highest

find_local_maxima((32.0005,116.9999))

def temp_pick_highest_three(latlong):
    """temp functions for getting pins to put on map"""

    master_array = create_master_array(latlong)
    # radius_array = set_radius(latlong, master_array)
    highest = find_local_maxima(latlong)

    top_three = ([(highest[0][0], highest[1][0]), 
                  (highest[0][1], highest[1][1]),
                  (highest[0][2], highest[1][2])])
    print "AHhHHH"
    print top_three
    return top_three

temp_pick_highest_three((32.0005,116.9999))

def check_obstructions_west(index):
    """Check that there are no obstructions to the west given an index"""
    pass

def check_min_viewing_angle(index):
    """Check that the angle to the horizon meets the min angle requirement"""
    pass

def conver_point_to_latlong(latlong):
    """Given a tuple of indexes for a point, calculate the latlong of that point.

    Reference the database for exact coordinates"""



    file_exact_coordinates = LatLong.query.filter_by(filename=filename).one()


    pass
