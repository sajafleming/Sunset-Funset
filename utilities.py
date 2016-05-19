""" Functions that know how to function """

from osgeo import gdal
from math import ceil
import scipy
import scipy.signal
import numpy as np
import os
from scipy.ndimage.filters import generic_filter as gf
from flask_sqlalchemy import SQLAlchemy
# from model import connect_to_db, db, LatLong
from operator import itemgetter

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
    w = int(ceil(abs(latlong[1]))) # will always return a postive integer

    filename = "n%sw%s.img" % (n, w)

    return filename, n, w 

def validate_location_for_search(latlong):
    """Test to see if the user entered a location that is out of the range of 
    data for this app (out of the US)
    """

    filename, n, w = find_tile_name(latlong)

    filepath = create_filepath(filename)

    if os.path.isfile(filepath):
        return True
    else:
        return False
    
def create_filename(n, w):
    """Given n and w, create a filename string"""

    return "n%sw%s.img" % (n, w)

def create_filepath(filename):
    """Create filepath for a given .img file"""

    return DEFAULT_IMG_FILE_ROOT + filename

    # TODO: split this funtion into two functions. One that just returns n and w and 
    # one that generates the file name. This will get rid of repetition below

def generate_filenames(latlong):
    """Generate filenames dictionary of surrounding tiles for a given latlong.

    The key of the dictionary represents where that tile is located in terms of
    the center tile (the tile that contains the given latlong).
    """

    filename, n, w = find_tile_name(latlong)

    filenames = ({ "NW": create_filename(n + 1, w + 1),
                   "N": create_filename(n + 1, w),
                   "NE": create_filename(n + 1, w - 1),
                   "W": create_filename(n, w + 1),
                   "C": create_filename(n, w),
                   "E": create_filename(n, w - 1),
                   "SW": create_filename(n - 1, w + 1),
                   "S": create_filename(n - 1, w),
                   "SE": create_filename(n - 1, w - 1)})

    print "##########################################"
    print filenames

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

        filepath = DEFAULT_IMG_FILE_ROOT + filename_dict[file_key] # TODO: move folder string to a constant

        # check to make sure the file exists
        if os.path.isfile(filepath):
            # print filename
            # Append the array to a dictionary with the same key
            img_data_dict[file_key] = read_img_file(filepath)
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

# def exact_coordinate_from_db(filename="n33w117"):
#     """Find exact NW coordinate for a given latlong"""

#     file_exact_coordinates = db.session.query(LatLong).filter_by(filename=filename).all()

#     # LatLong.query.filter_by(filename=filename).all()

#     # (db.session.query(User).filter(User.username == username).count())

#     print file_exact_coordinates[0]

# print "HELLO HERE I AM"
# exact_coordinate_from_db()

# | filename |     w_bound     |     e_bound     |    n_bound     |    s_bound
# | n38w118  | -118.0016666667 | -116.9983333333 | 38.00166666667 | 36.99833333333
# will be upper left corner of master array

def find_coordinates(latlong, master_array_n_bound, master_array_w_bound):
    """Find index for a latlong given the exact N and W bounds.

    Latitude_Resolution: 0.00001
    Longitude_Resolution: 0.00001
    """

    # I think the actual bounds are close enough to not have to query the database 
    # get the exact values, since the indices are rounded anyway

    lat = latlong[0]
    lng = latlong[1]

    # check absolute values 
    y_coordinate = int(round(abs((master_array_n_bound - lat) / DEGREES_PER_INDEX)))
    x_coordinate = int(round(abs(master_array_w_bound - lng)) / DEGREES_PER_INDEX)

    return (y_coordinate, x_coordinate)

# create_master_array((32.0005,116.9999))
# /Users/Sarah/PROJECT/imgfiles/n33w117.img

def set_radius(latlong, master_array, master_array_n_bound, master_array_w_bound):
    """Narrow down the master array to approximately a 20 mile radius (1032 entries).

    Center of radius: (a,b) or the latlong the user entered. The values of the 2D
    array within the radius will remain their original value and the values outside
    of the radius will become zero. This is done using a mask. An array just outside
    the radius will be returned along with the NW (top left) coordinate of the 
    new array. The radius array dimensions will be 2065 x 2065.
    """

    y_coordinate, x_coordinate = find_coordinates(latlong, master_array_n_bound, master_array_w_bound)
    print "COORDINATES:"
    print y_coordinate, x_coordinate

    # VisibleDeprecationWarning: boolean index did not match indexed array along 
    # dimension 0; dimension is 10836 but corresponding boolean dimension is 10835
    n = 10836
    r = 1032

    # TODO: comment this
    y,x = np.ogrid[-y_coordinate:n-y_coordinate, -x_coordinate:n-x_coordinate]
    mask = x**2 + y**2 > r**2

    master_array[mask] = 0


    # [y-r:y+r+1][x-r:x+r+1] row, column
    # print y_coordinate
    # print x_coordinate
    y_begin = max(y_coordinate - r, 0)
    y_end = y_coordinate + r + 1
    x_begin = max(x_coordinate - r, 0)
    x_end = x_coordinate + r + 1
    # print y_begin, y_end
    # print x_begin, x_end
    radius_array = master_array[y_begin:y_end, x_begin:x_end]

    cropped_array_top_left_coordinates = (y_begin, x_begin)

    print "CROP INCICES:"
    print x_begin, x_end, y_begin, y_end

    # cropped or reduced / masked_elevation_array elevation_array
    # also change the name of this function to crop array

    print "TOP LEFT COORDINATES:"
    # print radius_array
    print cropped_array_top_left_coordinates
    return radius_array, cropped_array_top_left_coordinates

# set_radius((32.0005,116.9999))

def find_local_maxima(latlong, master_array_n_bound, master_array_w_bound):
    """Find local maxima of 2D array and return their positions.

    The format of the returned coordinates is (array([row1, row2]), (array[column1, column2])

    TEST
    -----
    >>> y = np.array([[1, 2, 1, 2],
    ...               [2, 2, 0, 0],
    ...               [5, 3, 4, 4]])
    >>> argrelmax(y, axis=1)
    (array([0]), array([1]))
    """
    # use algorithm below
    # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax
    master_array = create_master_array(latlong)
    print master_array

    radius_array, cropped_array_top_left_coordinates = set_radius(latlong, master_array, master_array_n_bound, master_array_w_bound)
    print radius_array
    print "helloooooo ^^^^"

    # TODO: change name, highest is not descriptive
    highest = scipy.signal.argrelmax(radius_array)

    coordinates_with_elevations = []

    for i in range(len(highest[0])):

        elevation = elevation_by_coordinates((highest[0][i],highest[1][i]), radius_array)

        if elevation > 0 and check_candidate_local_maximum((highest[0][i], highest[1][i]), radius_array):

            coordinates_with_elevations.append(((highest[0][i],highest[1][i]), elevation))
        

    print "HIGHEST POINTS:"
    print coordinates_with_elevations[0:101]
    return coordinates_with_elevations, radius_array, cropped_array_top_left_coordinates

# find_local_maxima((36.79, -117.05))

BOUNDING_BOX_WIDTH = 20

def check_candidate_local_maximum(candidate_point, radius_array):
    """Check to see if realative maximum is realative max over an area of _______

    10 indices for now
    """

    rows_lower_bound = -(BOUNDING_BOX_WIDTH / 2) + candidate_point[0]
    rows_upper_bound = candidate_point[0] + (BOUNDING_BOX_WIDTH / 2)
    column_lower_bound = -(BOUNDING_BOX_WIDTH / 2) + candidate_point[1]
    column_upper_bound = candidate_point[1] + (BOUNDING_BOX_WIDTH / 2)

    # maybe change the following by passing the elevation with the candidate point?
    candidate_elevation = elevation_by_coordinates(candidate_point, radius_array) 

    # TODO: split logic up to make it cleaner 
    for row in range(max((rows_lower_bound), 0), min(rows_upper_bound, len(radius_array))):
        for column in range(max(column_lower_bound, 0), min(column_upper_bound, len(radius_array))):

            # print radius_array[row][column], candidate_elevation
            if radius_array[row][column] > candidate_elevation:
                return False
    
    return True


def elevation_by_coordinates(coordinates, radius_array=None):
    """Search the radius array by coordinates and return the elevation at that point

    [row, column]
    """

    # FOR TESTING
    # radius_array = np.array([[ 1,  2,  1,  2],
    #                          [ 2,  2,  0,  0],
    #                          [ 3, 15,  4,  4]]) 

    elevation = radius_array[coordinates[0], coordinates[1]]

    # print "elevation is %s" % (elevation)
    return elevation


def sort_by_elevation(coordinates_with_elevations, radius_array=None):
    """Sort coordinates in descending order by highest elevation.

    Highest is a tuple of arrays that correspond TODO
    Use itemgetter from the operator library to sort in place. Will return a 
    list of tuples of the following format: [((row, column), elevation)]
    """

    # for testing
    # highest = (np.array([0, 2]), np.array([1, 1]))

    # moved the following to find_local_maxima
    # elevations = []
    # for i in range(len(highest[0])):
    #     elevation = elevation_by_coordinates((highest[0][i],highest[1][i]), radius_array)
    #     if elevation > 0:
    #         elevations.append(((highest[0][i],highest[1][i]), elevation))

    # sort by second value of tuples
    coordinates_with_elevations.sort(key=itemgetter(1), reverse=True)

    top_100_elevations = coordinates_with_elevations[0:101]

    print "SORTED ELEVATIONS"
    print top_100_elevations
    return top_100_elevations

# highest, radius_array = find_local_maxima((36.79, -117.05))
# top_100_elevations = sort_by_elevation(highest, radius_array)
# sort_by_elevation()


def check_obstructions_west(candidate_point, radius_array):
    """Check that there are no obstructions to the west given an index

    candidate_point is in the form ((row, column), elevation)
    """

    # check this to make sure it's doing what I want
    
    candidate_point = ((1312, 621), 2344.2751)
    # only testing current row now, might want to add above and below
    row_index_constant = candidate_point[0][0]
    candidate_point_elevation = candidate_point[1]

    # look 100 indices to the left of candidate point
    for column_index in range(max(-100 + candidate_point[0][1], 0), candidate_point[0][1]):
        
        # print radius_array[column_index,row_index_constant]
        
        # check to see if any of the points are higher than the candidate point
        if radius_array[row_index_constant, column_index] > candidate_point_elevation:

            return False

    return True

def convert_to_latlong(coordinate, master_array_n_bound, master_array_w_bound, cropped_array_top_left_coordinates):
    """Given a tuple of indexes for a point, calculate the latlong of that point.

    Uses exact coordinates from db"""

    OFFSET = cropped_array_top_left_coordinates

    # row of coordinate plus row of offset
    master_array_row_index = OFFSET[0] + coordinate[0]
    master_array_column_index = OFFSET[1] + coordinate[1]

    lat_final = master_array_n_bound - master_array_row_index * DEGREES_PER_INDEX
    long_final = master_array_w_bound + master_array_column_index * DEGREES_PER_INDEX
    # master_array_w_bound should be negative here
    # add because it will be greater to the right

    print "FINAL COORDINATES:"
    print (lat_final, long_final)
    return (lat_final, long_final)


def pick_n_best_points(latlong, master_array_n_bound, master_array_w_bound, n=15):
    """Pick n of the best sunset viewing spot candidate

    Returns coordinates without elevation
    """

    coordinates_with_elevations, radius_array, cropped_array_top_left_coordinates = find_local_maxima(latlong, master_array_n_bound, master_array_w_bound)

    top_100_elevations = sort_by_elevation(coordinates_with_elevations, radius_array)

    n_points_latlongs = []

    for candidate_point in coordinates_with_elevations:

        if check_obstructions_west(candidate_point, radius_array) and len(n_points_latlongs) < n:
            n_points_latlongs.append(candidate_point[0])

    final_latlongs = []

    for final_point in n_points_latlongs:

        final_latlongs.append(convert_to_latlong(final_point, master_array_n_bound, master_array_w_bound, cropped_array_top_left_coordinates))

    print "N POINTS"
    print final_latlongs
    return final_latlongs


pick_n_best_points((36.79, -117.05), 38.00166666667, -118.0016666667)


