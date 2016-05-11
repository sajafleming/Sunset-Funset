# functions that know how to function

from osgeo import gdal
from math import ceil
import scipy
from numpy import zeros_like
import os



def find_starting_tile_name(latlong):
    """Find the filename that includes the latlong that the user inputed"""
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
    # filenames = (["n%sw%s.img" % (n, w),
    #               "n%sw%s.img" % (n, w + 1),
    #               "n%sw%s.img" % (n - 1, w + 1),
    #               "n%sw%s.img" % (n - 1, w),
    #               "n%sw%s.img" % (n - 1, w - 1),
    #               "n%sw%s.img" % (n, w -1),
    #               "n%sw%s.img" % (n + 1, w - 1),
    #               "n%sw%s.img" % (n + 1, w),
    #               "n%sw%s.img" % (n + 1, w + 1),])


    # create list of filenames of the surrounding img files
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

    print arr
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

    center_tile, n, w = find_starting_tile_name(latlong)

    # filenames_list = generate_filenames_list(n, w)
    # print filenames_list

    filename_dict = generate_filenames_list(n, w)

    for file_key in filename_dict:
        # create file path for particular filename
        filename = "/Users/Sarah/PROJECT/imgfiles/" + filename_dict[file_key]
        if os.path.isfile(filename):
            # print filename
            filename_dict[file_key] = read_img_file(filename)
        else:
            # make array of all zeros if file doesn't exist
            # using an array from a file I know exists to know what dimensions are
            look_alike = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img")

            #use this array to make a look alike - will have same dimensions with all zeros
            filename_dict[file_key] = zeros_like(look_alike)

    master_array = (scipy.vstack((
                           scipy.hstack((filename_dict[0], filename_dict[1], filename_dict[2])),
                           scipy.hstack((filename_dict[3], filename_dict[4], filename_dict[5])),
                           scipy.hstack((filename_dict[6], filename_dict[7], filename_dict[8]))
                          )))
    return master_array


create_master_array((32.0005,116.9999))
# /Users/Sarah/PROJECT/imgfiles/n33w117.img

def horizontal_array_stack(index1, index2):
    """Stack arrays horizontally [a] and [b] become [a][b]"""

def vertical_array_stack(index1, index2):
    """Stack arrays vertically [a] and [b] become [a]
                                                  [b] 
    """

def find_local_max(array):
    """Find local maximums of 2D array and return indexes."""
    # use algorithm below
    # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax
    pass

def check_obstructions_west(index):
    """Check that there are no obstructions to the west given an index"""
    pass

def check_min_viewing_angle(index):
    """Check that the angle to the horizon meets the min angle requirement"""
    pass
