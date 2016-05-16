""" Functions that know how to function """

from osgeo import gdal
from math import ceil
import scipy
import scipy.signal
import numpy as np
import os
from scipy.ndimage.filters import generic_filter as gf
from flask_sqlalchemy import SQLAlchemy

DEFAULT_IMG_FILE_ROOT = "/Users/Sarah/PROJECT/imgfiles/"

DEGREES_PER_INDEX = 0.0002777777777685509


def find_tile_name(latlong):
    """Find the filename that includes the given latlong. Return latlong and
    the n and w integer values.

    The topographical data is of 1-arc-second resolution so each tile has a 
    rounded integer name of the corresponding NW coordinate. Note the exact 
    coordinates of every tile is stored in a database.
    """

    # The ceiling of the latlong coordinate will give you the filename that contains it
    n = int(ceil(latlong[0]))
    w = abs(int(ceil(latlong[1])))

    filename = "n%sw%s.img" % (n, w)

    return filename, n, w

    # TODO: split this funtion into two functions. One that just returns n and w and 
    # one that generates the file name. This will get rid of repetition below

def generate_filenames(latlong):
    """Generate filenames dictionary of surrounding tiles for a given latlong.

    The key of the dictionary represents where that tile is located in terms of
    the center tile (the tile that contains the given latlong).
    """

    filename, n, w = find_tile_name(latlong)

    filenames = ({ "NW": "n%sw%s.img" % (n + 1, w - 1),
                   "N": "n%sw%s.img" % (n + 1, w),
                   "NE": "n%sw%s.img" % (n + 1, w + 1),
                   "W": "n%sw%s.img" % (n, w - 1),
                   "C": filename,
                   "E": "n%sw%s.img" % (n, w + 1),
                   "SW": "n%sw%s.img" % (n - 1, w - 1),
                   "S": "n%sw%s.img" % (n - 1, w),
                   "SE": "n%sw%s.img" % (n - 1, w + 1)})

    # print filenames
    return filenames


def read_img_file(file_path):
    """Read .img file as 2D array given a file path. 

    The .img files are a raster data type. The osgeo library provides a way to 
    open these files and read them as a numpy 2D array. 
    """

    geo = gdal.Open(file_path)
    # print geo
    # print type(geo)
    arr = geo.ReadAsArray()

    # print arr
    return arr

# def read_surrounding_tiles(latlong):
#     """Create array from img files. Return a numpy array with GDAL.
#     return arrays surrounding as well."""

def create_master_array(latlong, img_file_root=DEFAULT_IMG_FILE_ROOT):
    """Create a master array containing all arrays surrounding the given latlong.

    The array will be constructed from the dictionary of filenames with the keys
    in the following structure:

    [NW][N][NE]
     [W][C][E]
    [SW][S][SE]
    """

    filename_dict = generate_filenames(latlong)

    img_data_dict = {}

    for file_key in filename_dict:

        file_path = "/Users/Sarah/PROJECT/imgfiles/" + filename_dict[file_key] # TODO: move folder string to a constant

        if os.path.isfile(file_path):
            # print filename
            # Append the array to a dictionary with the same key
            img_data_dict[file_key] = read_img_file(file_path)
        else:
            # Make array of all zeros if file doesn't exist
            # Using an array from a file I know exists to know what dimensions are
            look_alike = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img") # TODO: move n33w117.img to a constant

            # Use this array to make a look alike - will have same dimensions with all zeros
            img_data_dict[file_key] = np.zeros_like(look_alike) # TODO: hardcode dimensions and use np.zeros() here

    # TODO: add a comment describing what's going on here.
    master_array = (scipy.vstack((
                           scipy.hstack((img_data_dict["NW"], img_data_dict["N"], img_data_dict["NE"])),
                           scipy.hstack((img_data_dict["W"], img_data_dict["C"], img_data_dict["E"])),
                           scipy.hstack((img_data_dict["SW"], img_data_dict["S"], img_data_dict["SE"]))
                          )))
    return master_array

def exact_coordinate_from_db(latlong):
    """Find exact NW coordinate for a given latlong"""

    file_exact_coordinates = LatLong.query.filter_by(filename=filename).one()

    pass

# | filename |     w_bound     |     e_bound     |    n_bound     |    s_bound
# | n38w118  | -118.0016666667 | -116.9983333333 | 38.00166666667 | 36.99833333333
# will be upper left corner of master array

def find_coordinates(latlong, n_bound=38.00166666667, w_bound=-118.0016666667):
    """Find index for a latlong given the exact N and W bounds.

    Latitude_Resolution: 0.00001
    Longitude_Resolution: 0.00001
    """

    lat = latlong[0]
    lng = latlong[1]

    y_coordinate = int(round(abs((n_bound - lat) / DEGREES_PER_INDEX)))
    x_coordinate = int(round(abs((w_bound - lng) / DEGREES_PER_INDEX)))

    return (y_coordinate, x_coordinate)

# create_master_array((32.0005,116.9999))
# /Users/Sarah/PROJECT/imgfiles/n33w117.img

def set_radius(latlong, master_array, n_bound=38.00166666667, w_bound=-118.0016666667):
    """Narrow down the master array to approximately a 20 mile radius (1032 entries).

    Center of radius: (a,b) or the latlong the user entered. The values of the 2D
    array within the radius will remain their original value and the values outside
    of the radius will become zero. This is done using a mask. An array just outside
    the radius will be returned along with the NW (top left) coordinate of the 
    new array.
    """

    # master_array = create_master_array((32.0005,116.9999))

    lat = ceil(latlong[0])
    lng = ceil(latlong[1])

    # VisibleDeprecationWarning: boolean index did not match indexed array along 
    # dimension 0; dimension is 10836 but corresponding boolean dimension is 10835
    n = 10836
    r = 1032

    # TODO: comment this
    # y,x = np.ogrid[-lat:n-lat, -lng:n-lng]
    # mask = x**2 + y**2 > r**2

    # master_array[mask] = 0

    y_coordinate, x_coordinate = find_coordinates(latlong, n_bound, w_bound)

    # [y-r:y+r+1][x-r:x+r+1] row, column
    print y_coordinate
    print x_coordinate
    y_begin = max(y_coordinate - r, 0)
    y_end = y_coordinate + r + 1
    x_begin = max(x_coordinate - r, 0)
    x_end = x_coordinate + r + 1
    print y_begin, y_end
    print x_begin, x_end
    radius_array = master_array[y_begin:y_end, x_begin:x_end]

    # H M M M M M M M M M M M M

    print radius_array
    return radius_array

# set_radius((32.0005,116.9999))

def find_local_maxima(latlong, db=None):
    """Find local maxima of 2D array and return their positions."""
    # use algorithm below
    # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax
    master_array = create_master_array((36.79, -117.05))

    radius_array = set_radius(latlong, master_array)

    highest = scipy.signal.argrelmax(radius_array)

    print "AHHH"
    print highest
    return master_array

find_local_maxima((36.79, -117.05))

# def temp_pick_highest_three(latlong):
#     """temp functions for getting pins to put on map

#     DELETE ME
#     """

#     master_array = create_master_array(latlong)
#     # radius_array = set_radius(latlong, master_array)
#     highest = find_local_maxima(latlong)

#     top_three = ([(highest[0][0], highest[1][0]), 
#                   (highest[0][1], highest[1][1]),
#                   (highest[0][2], highest[1][2])])
#     print "AHhHHH"
#     print top_three
#     return top_three

# temp_pick_highest_three((32.0005,116.9999))

def check_obstructions_west(index):
    """Check that there are no obstructions to the west given an index"""
    pass

def check_min_viewing_angle(index):
    """Check that the angle to the horizon meets the min angle requirement"""
    pass

def convert_to_latlong(coordinates):
    """Given a tuple of indexes for a point, calculate the latlong of that point.

    Reference the database for exact coordinates"""



    file_exact_coordinates = LatLong.query.filter_by(filename=filename).one()


    pass
