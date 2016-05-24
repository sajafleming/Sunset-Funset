""" Functions that know how to function """

from osgeo import gdal
from math import ceil
import scipy
import scipy.signal
import numpy as np
import os
from scipy.ndimage.filters import generic_filter as gf
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter

DEFAULT_IMG_FILE_ROOT = "/Users/Sarah/PROJECT/imgfiles/"

DEGREES_PER_INDEX = 0.0002777777777685509

# add comment
OVERLAPPING_INDICES = 12


def pick_n_best_points(latlong, elevation_array_n_bound, elevation_array_w_bound, user_radius=20, n=15):
    """Pick n of the best sunset viewing spot candidates. 

    The function first pulls surrounding latlong data into memory. Next, the data
    is filtered to local maximums without obstructions to the wet. Next, those
    remaining points are given a score based on their elevation and how much they
    resemble a cliff or dropoff. The candidate points are then ranked and sorted
    by ranking and the first n are converted to latlong.

    Returns n latlongs, representing the best n sunset viewing spots. 
    """

    # Create array with elevation data surrounding the user's inputte latlong
    elevation_array = create_elevation_array(latlong)

    # Convert the user's radius to number of indices for cropping
    radius = convert_radius_to_number_of_indices(user_radius)

    # Begin filter process:
    # 1. filter out any point that is not a local maxima over a certain area
    candidates_with_elevations, cropped_elevation_array, cropped_array_top_left_indices \
     = find_local_maxima(latlong, elevation_array, elevation_array_n_bound, elevation_array_w_bound, radius)


    # 2. filter remaining candidates by checking obstructions to the west
    #candidates_with_elevations = [candidate for candidate in candidates_with_elevations if is_unobstructed_west(candidate, cropped_elevation_array)]
    # for candidate in candidates_with_elevations:
    #     # If the elements are obstructed, remove them from the candidates list
    #     if not is_unobstructed_west(candidate, cropped_elevation_array):
    #         candidates_with_elevations.remove(candidate)
    #         print candidate

    # Compute all scores (elevation is already a score)
    # All scores are stored in a list

    print "Num candidates after obstruction filtering = {}".format(len(candidates_with_elevations))
    # Create new list to store all the scores
    candidates_with_all_scores = []

    # Add cliff score to candidate_point tuple
    for candidate_point in candidates_with_elevations:

        cliff_score = get_cliff_score(candidate_point, cropped_elevation_array)

        candidates_with_all_scores.append((candidate_point[0], [candidate_point[1], cliff_score]))
    
    # Rank points - rank function only returns top 100
    ranked_points = rank_candidate_points(candidates_with_all_scores)
    print "First 100 candidate points sorted by rank"
    print ranked_points

    # Finally, convert these last points to latlongs
    final_latlongs = []

    # Convert n ranked points to latlongs
    for final_point in ranked_points[:n]:

        final_latlongs.append(convert_to_latlong(final_point[0], elevation_array_n_bound, elevation_array_w_bound, cropped_array_top_left_indices))

    print "N POINTS"
    print final_latlongs
    return final_latlongs


def create_elevation_array(latlong, img_file_root=DEFAULT_IMG_FILE_ROOT):
    """Create a master array containing all arrays surrounding the given latlong.

    The array will be constructed from the dictionary of filenames with the keys
    in the following structure:

    [NW][N][NE]
     [W][C][E]
    [SW][S][SE]

    The .img files have an overlap of approx. 11.999999880419653 indices. To 
    reconcile this, slice the OVERLAPPING_INDICES off the south and east bounds.

    This will return an array with dimensions of 10,800 * 10,800
    """

    # Create the filename dict where the keys correspond to the location in elevation array
    filename_dict = generate_surrounding_filenames(latlong)

    # Instantiate a new dictionary with the arrays as values
    img_data_dict = {}

    for file_key in filename_dict:

        filepath = DEFAULT_IMG_FILE_ROOT + filename_dict[file_key]

        # Check to make sure the file exists
        if os.path.isfile(filepath):
            
            # Add the array to a dictionary with the same key and crop by 12 on right and bottom
            img_data_dict[file_key] = read_img_file(filepath)[:-OVERLAPPING_INDICES,:-OVERLAPPING_INDICES]
        else:
            # Make array of all zeros if file doesn't exist
            # Using an array from a file I know exists to know what dimensions are
            look_alike = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img") # TODO: move n33w117.img to a constant

            # Use this array to make a look alike - will have same dimensions with all zeros
            img_data_dict[file_key] = np.zeros_like(look_alike)[:-OVERLAPPING_INDICES,:-OVERLAPPING_INDICES] # TODO: hardcode dimensions and use np.zeros() here

    # Use scipy to vertically concatenate 3 rows that have been horizontally concatenated
    elevation_array = (scipy.vstack((
                           scipy.hstack((img_data_dict["NW"], img_data_dict["N"], img_data_dict["NE"])),
                           scipy.hstack((img_data_dict["W"], img_data_dict["C"], img_data_dict["E"])),
                           scipy.hstack((img_data_dict["SW"], img_data_dict["S"], img_data_dict["SE"]))
                          )))

    return elevation_array


def convert_radius_to_number_of_indices(user_radius):
    """Take the mileage that the user inputted and conver to how many
    indices if would represent. 

    Each index represents approximately .0186411357696567 miles
    """

    radius = int(float(user_radius) / .0186411357696567)
    print "AHHHH"
    print radius

    return radius


def find_filename(latlong):
    """Find the filename of the file that includes data for the given latlong. 
    Return latlong and the n and w integer values in the filename.

    The topographic data is 1-arc-second of resolution and each file has a 
    rounded integer name of the corresponding NW coordinate. Note the exact NESW
    bounds of every tile are stored in a database.

    If the given latlong is (37.7749, 122.4194)) the function will 
    return ("n38w123.img", 38, 123)
    """

    # The ceiling of the lat coordinate will give the n int value in the filename
    n = int(ceil(latlong[0]))
    # The actually long is negative but the files are named as postitive integers
    # so take the abs value of the coordinate before the ceiling 
    w = int(ceil(abs(latlong[1]))) # will always return a postive integer

    filename = "n%sw%s.img" % (n, w)

    print filename, n, w
    return filename, n, w 

# TODO: split this funtion into two functions. One that just returns n and w and 
# one that generates the file name. This will get rid of repetition below

def validate_location_for_search(latlong):
    """Test to see if the user entered a location that is out of the range of 
    data for this app (out of the US).

    If the filepath does not exist, then there is no data for that area.
    """

    filename, n, w = find_filename(latlong)

    filepath = create_filepath(filename)

    if os.path.isfile(filepath):
        return True
    else:
        return False
    
def create_filename(n, w):
    """Given integer n and w coordinates, create a filename string"""

    return "n%sw%s.img" % (n, w)

def create_filepath(filename):
    """Create filepath for a given .img file"""

    return DEFAULT_IMG_FILE_ROOT + filename


def generate_surrounding_filenames(latlong):
    """Generate dictionary of filenames for the surrounding data for a given 
    latlong.

    The key of the dictionary represents where that tile is located in terms of
    the center tile (the tile that contains the original latlong).
    """

    filename, n, w = find_filename(latlong)

    filenames = ({ "NW": create_filename(n + 1, w + 1),
                   "N": create_filename(n + 1, w),
                   "NE": create_filename(n + 1, w - 1),
                   "W": create_filename(n, w + 1),
                   "C": create_filename(n, w),
                   "E": create_filename(n, w - 1),
                   "SW": create_filename(n - 1, w + 1),
                   "S": create_filename(n - 1, w),
                   "SE": create_filename(n - 1, w - 1)})

    return filenames


def read_img_file(filepath):
    """Read .img file as 2D numpy array given a filepath. 

    The .img files are raster data. The osgeo library provides a way to 
    open these files and read them as a numpy 2D array.

    Each array of 1 arc second should have dimensions 3612 x 3612. 
    """

    geo = gdal.Open(filepath)
   
    arr = geo.ReadAsArray()

    return arr



# sample from database
# | filename |     w_bound     |     e_bound     |    n_bound     |    s_bound
# | n38w118  | -118.0016666667 | -116.9983333333 | 38.00166666667 | 36.99833333333

def find_coordinates(latlong, elevation_array_n_bound, elevation_array_w_bound):
    """Find index for elevation array of a given latlong.

    The indices will be calculated with the exact N and W bounds from the database. 
    DEGREES_PER_INDEX is calculated by taking the difference of NS (or EW) bounds
    and dividing 3612 (the length and width of a single file). DEGREES_PER_INDEX
    is calculated to be 0.0002777777777685509.
    """

    lat = latlong[0]
    lng = latlong[1]

    # check absolute values 
    y_index = int(round(abs((elevation_array_n_bound - lat) / DEGREES_PER_INDEX)))
    x_index = int(round(abs((elevation_array_w_bound - lng) / DEGREES_PER_INDEX)))

    return (y_index, x_index)

# create_elevation_array((32.0005,116.9999))
# /Users/Sarah/PROJECT/imgfiles/n33w117.img

# RADIUS = 1073 / 2

def crop_elevation_array(latlong, elevation_array, elevation_array_n_bound, elevation_array_w_bound, radius):
    """Crop the elevation_data_array to approximately a 20 mile radius (1073 entries:
    each index represents approximately .0186411357696567 miles)
    around the given latlong.

    The latlong the user entered will be the center of the radius. The values of 
    the 2D array within the radius will remain their original value and the values 
    outside of the radius will be changed to -1000, an arbitrary low number.
    This is done using a mask. An array just outside this radius will be returned 
    along with the NW (top left) coordinate of the new array. The radius array 
    dimensions will be 2146 x 2146.
    """

    # Coordinates for user entered point in terms of master array
    y_index, x_index = find_coordinates(latlong, elevation_array_n_bound, elevation_array_w_bound)
    #print "COORDINATES:"
    #print y_index, x_index

    n = len(elevation_array)
    # r = radius

    # TODO: comment this
    # y,x = np.ogrid[-y_index:n-y_index, -x_index:n-x_index]
    # mask = x**2 + y**2 > radius**2

    # elevation_array[mask] = -1000

    # Creating the box around the radius by setting a beginning and ending point
    y_begin = max(y_index - radius, 0)
    y_end = y_index + radius + 1
    x_begin = max(x_index - radius, 0)
    x_end = x_index + radius + 1
   
    cropped_elevation_array = elevation_array[y_begin:y_end, x_begin:x_end]

    cropped_array_top_left_indices = (y_begin, x_begin)

    # Find the postion of the user's latlong by offesetting the cropped array
    user_latlong_coordinates_cropped = (y_index - y_begin, x_index - x_begin)

    #print "CROP INCICES:"
    #print x_begin, x_end, y_begin, y_end

    #print "TOP LEFT COORDINATES:"
    # print cropped_elevation_array
    #print cropped_array_top_left_indices
    return cropped_elevation_array, cropped_array_top_left_indices, user_latlong_coordinates_cropped

# crop_elevation_array((32.0005,116.9999))


def find_local_maxima(latlong, elevation_array, elevation_array_n_bound, elevation_array_w_bound, radius):
    """Find local maxima of 2D array and return positions in array.

    The format of the returned coordinates is (array([row1, row2]), (array[column1, column2]). 
    The algorithm used to find local maxima is argrelmax which belongs to the 
    scipy.signal library. The argrelmax returns values where ``comparator(data[n], data[n+1:n+order+1])``
    is True. For more info see http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax

    TEST
    -----
    >>> y = np.array([[1, 2, 1, 2],
    ...               [2, 2, 0, 0],
    ...               [5, 3, 4, 4]])
    >>> argrelmax(y, axis=1)
    (array([0]), array([1]))

    For every point returned by argrelmax, check if local maxima condition still
    true when looking at an area of about FIXME BOUNDING_BOX_WIDTH

    The function returns all local maximums in a list in the form:
    [((row, column), relative_elevation), ... ]

    Elevation realative to starting point.
    """

    cropped_elevation_array, cropped_array_top_left_indices, user_latlong_coordinates = \
        crop_elevation_array(latlong, elevation_array, elevation_array_n_bound, elevation_array_w_bound, radius)

    local_maxima = scipy.signal.argrelmax(cropped_elevation_array)

    print "Num local_maxima from scipy = {}".format(len(local_maxima[0]))
    # Find the elevation of the point that the user entered
    elevation_of_center = elevation_by_indices(user_latlong_coordinates, cropped_elevation_array)
    candidates_with_elevations = []

    # Loop over every point returned in argrelmax and do further analysis:
    for i in xrange(len(local_maxima[0])):

        # For each local max indices given, find the corresponding elevation
        elevation = elevation_by_indices((local_maxima[0][i], local_maxima[1][i]), cropped_elevation_array)

        # Throw out all negative elevations they are not good for watching sunsets :)
        # Check each candidate local maxima to see if it is also a maxima for 
        # the area around it. If these conditions are met, append it to the list
        # of coordinates with elevations.
        if elevation > 0 and is_local_maximum((local_maxima[0][i], local_maxima[1][i]), cropped_elevation_array):

            # Difference between user's entered location and the points elevation
            # relative_elevation = elevation - elevation_of_center

            candidates_with_elevations.append(((local_maxima[0][i],local_maxima[1][i]), elevation))
        

    #print "local_maxima POINTS:"
    #print candidates_with_elevations[0:101]
    return candidates_with_elevations, cropped_elevation_array, cropped_array_top_left_indices

# find_local_maxima((36.79, -117.05))

# use for testing
# BOUNDING_BOX_WIDTH = 50

# USE ME
BOUNDING_BOX_WIDTH = 100

def is_local_maximum(candidate_point, cropped_elevation_array):
    """Check to see if realative maximum is realative max over an area of FIXME

    10 indices for now
    """

    rows_lower_bound = -(BOUNDING_BOX_WIDTH / 2) + candidate_point[0]
    rows_upper_bound = candidate_point[0] + (BOUNDING_BOX_WIDTH / 2)
    column_lower_bound = -(BOUNDING_BOX_WIDTH / 2) + candidate_point[1]
    column_upper_bound = candidate_point[1] + (BOUNDING_BOX_WIDTH / 2)

    rows_for_checking_start = max((rows_lower_bound), 0)
    rows_for_checking_end = min(rows_upper_bound, len(cropped_elevation_array))
    columns_for_checking_start = max(column_lower_bound, 0) 
    columns_for_checking_end = min(column_upper_bound, len(cropped_elevation_array))

    # maybe change the following by passing the elevation with the candidate point?
    candidate_elevation = elevation_by_indices(candidate_point, cropped_elevation_array) 

    # TODO: comment and doc string
    for row in range(rows_for_checking_start, rows_for_checking_end):
        for column in range(columns_for_checking_start, columns_for_checking_end):

            # If the elevation of a point is greater than the elevation for the 
            # candidate point, return False meaning the candidate point will be 
            # thrown out as a local maxima. 
            if cropped_elevation_array[row][column] > candidate_elevation:
                return False
    
    return True


def elevation_by_indices(coordinates, cropped_elevation_array):
    """Search the cropped_elevation_array by coordinates and return the elevation 
    at that point.

    [row, column]
    """

    elevation = cropped_elevation_array[coordinates[0], coordinates[1]]

    # print "elevation is %s" % (elevation)
    return elevation


# for testing
# CHECK_WEST = 100
# ROWS_CHECK = 20

# USE ME
CHECK_WEST = 500
ROWS_CHECK = 5

def is_unobstructed_west(candidate_point, cropped_elevation_array):
    """Check that there are no obstructions to the west given an index

    Candidate_point is in the form ((row, column), elevation).
    """
    # check this to make sure it's doing what I want
    
    # only testing current row now, might want to add above and below
    row_index_constant = candidate_point[0][0]
    candidate_point_elevation = candidate_point[1]

    row_to_start_obs_check = max(-ROWS_CHECK + row_index_constant, 0)
    row_to_end_obs_check = min(row_index_constant + ROWS_CHECK, len(cropped_elevation_array))

    # TODO: comment this, change any candidate_point reference to variable name
    # for clarity
    # look 100 indices to the left of candidate point
    for row_index in range(row_to_start_obs_check, row_to_end_obs_check):
        for column_index in range(max(-CHECK_WEST + candidate_point[0][1], 0), candidate_point[0][1]):
            
            # print cropped_elevation_array[column_index,row_index_constant]
            
            # check to see if any of the points are higher than the candidate point
            if cropped_elevation_array[row_index, column_index] > candidate_point_elevation:

                return False

    return True

ROWS_FOR_DROPOFF = 5
COLUMNS_FOR_DROPOFF = 5

def get_cliff_score(candidate_point, cropped_elevation_array):
    """Check to see if there is a dropoff west of the candidate_point

    The score returned will be the ratio of candidate point to the average of 
    the other points. 
    Candidate_point is in the form ((row, column), elevation).
    """

    # Check a few columns next to point to see if the point is a "cliff", add cliff 
    # score to the scores list

    # Unlike is_candidate_local_maxima, this box only goes as far east as the
    # candidate point
    rows_lower_bound = -ROWS_FOR_DROPOFF + candidate_point[0][0]
    rows_upper_bound = candidate_point[0][0] + ROWS_FOR_DROPOFF
    column_lower_bound = -COLUMNS_FOR_DROPOFF + candidate_point[0][1]
    column_upper_bound = candidate_point[0][1]

    rows_for_checking_start = max(rows_lower_bound, 0)
    rows_for_checking_end = min(rows_upper_bound, len(cropped_elevation_array))
    columns_for_checking_start = max(column_lower_bound, 0) 
    columns_for_checking_end = column_upper_bound

    print "CANDIDATE POINT"
    print candidate_point
    candidate_elevation = candidate_point[1] 

    total_points = 0
    other_elevation_total = 0

    for row in range(rows_for_checking_start, rows_for_checking_end):
        for column in range(columns_for_checking_start, columns_for_checking_end):

            total_points += 1

            other_elevation_total += cropped_elevation_array[row][column]

    if total_points == 0:
        cliff_score = 0
    else:
        # Take the average of the checked region
        average_elevation_other = other_elevation_total / total_points

        # # If the average elevation is less than add the difference as the cliff_score
        # if average_elevation_other < candidate_elevation:
        
        # try cliffness proportional to absolute elevation- divide by candidate_point[1]
        cliff_score = (candidate_elevation - average_elevation_other)


    return cliff_score


def rank_candidate_points(candidate_points):
    """Using a candidate point's scores, return a ranking for how good of a
    sunset viewing spot the point is. Returns the top 100 ranked sunsets.

    Returns a list of tuples of coordinates with the indices and the calculated
    ranking. The list is sorted by ranking.
    """

    candidates_with_ranking = []
    candidates_score = 0

    for candidate_point in candidate_points:
        # print "HERE I AM"
        # print candidate_point

        elevation_score = candidate_point[1][0]
        cliffiness_score = candidate_point[1][1]
        print "ELEVATION SCORE"
        print elevation_score
        print "CLIFF SCORE"
        print cliffiness_score

        # Multiply the scores by weight to create a ranking number
        candidates_score = (elevation_score * .05) + (cliffiness_score * 0)
        # candidates_score = elevation_score * cliffiness_score

        # Add point and rank to a list
        candidates_with_ranking.append((candidate_point[0], candidates_score))

    # Sort list in descending order by ranking
    candidates_with_ranking.sort(key=itemgetter(1), reverse=True)

    return candidates_with_ranking[:100]


def convert_to_latlong(coordinate, elevation_array_n_bound, elevation_array_w_bound, cropped_array_top_left_indices):
    """Given a tuple of indicess for a point in the form (row, column), calculate
    the latlong of that point.

    Using the exact coordinates of the west and north bounds from the db, the 
    latlong is calculated based on the offset from the cropped elevation array.
    """

    OFFSET = cropped_array_top_left_indices

    # row of coordinate plus row of offset
    elevation_array_row_index = OFFSET[0] + coordinate[0]
    elevation_array_column_index = OFFSET[1] + coordinate[1]

    lat_final = elevation_array_n_bound - elevation_array_row_index * DEGREES_PER_INDEX
    long_final = elevation_array_w_bound + elevation_array_column_index * DEGREES_PER_INDEX
    # elevation_array_w_bound should be negative here
    # add because it will be greater to the right

    #print "FINAL COORDINATES:"
    #print (lat_final, long_final)
    return (lat_final, long_final)





# pick_n_best_points((36.79, -117.05), 38.00166666667, -118.0016666667)


