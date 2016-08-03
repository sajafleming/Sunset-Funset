"""Algorithms for finding optimal sunset viewing spots"""

import scipy
import scipy.signal
import numpy as np
import os
import time
import boto3
import botocore
from osgeo import gdal
from math import ceil
from scipy.ndimage.filters import generic_filter as gf
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter
from utilities import get_filename_n_w, create_filename, create_filepath

# TODO: possibly move all file manipulation to utilities
DEFAULT_IMG_FILE_ROOT = "/Users/Sarah/PROJECT/imgfiles/"
COLUMNS_CHECK_OBS_WEST = 500
ROWS_CHECK_OBS_WEST = 5
ROWS_FOR_DROPOFF = 5
COLUMNS_FOR_DROPOFF = 5
BOUNDING_BOX = 50

DEGREES_PER_INDEX = 0.0002777777777685509
# The .img files have an overlap of approx. 11.999999880419653 indices
OVERLAPPING_INDICES = 12
# Each index represents approximately .0186411357696567 miles
MILES_PER_INDEX = 0.0186411357696567

class SunsetViewFinder(object):
    """Find the best sunset viewing spots"""

    def __init__(self, latlong, elevation_array_n_bound, 
                 elevation_array_w_bound, radius, number_of_points_returned=25):
        self._latlong = latlong
        self._nbound = elevation_array_n_bound
        self._wbound = elevation_array_w_bound
        self._search_radius = radius
        self._number_of_points_returned = number_of_points_returned
        self._elevation_array = None 
        self._cropped_elevation_array = None
        self._cropped_array_top_left_indices = None
        self._user_latlong_coordinates = None
        self._radius_in_indices = None
        self._elevation_of_center = None
        # attribute for rootfilename

    def pick_best_points(self):
        """Pick the best sunset viewing spots of all possible candidates. 

        This method first pulls surrounding latlong data into memory from the 
        .img files. Next, surrounding data is cropped according to the search 
        radius. The function then finds the indices of local maximums within the
        radius and filters out the points that have obstructions to the west. 
        Next, the remaining points are given a score based on their elevation 
        realative to the original latlong and another score for how much they 
        resemble a cliff or dropoff. The candidate points are then ranked and 
        sorted by ranking. The points are then converted from indices to 
        latlongs. 

        Returns latlongs, representing the best sunset viewing spots. 
        """

        # Convert the search radius from miles to number of indices
        self._radius_in_indices = SunsetViewFinder._convert_radius_to_indices(
                                  self._search_radius)

        # Create a numpy 2D array with elevation data surrounding the user's 
        # inputted latlong
        self._elevation_array = self._create_elevation_array()

        # Crop the elevation array according to the search radius
        (self._cropped_elevation_array, self._cropped_array_top_left_indices, 
            self._user_latlong_coordinates) = self._crop_elevation_array()

        # Begin filter process:
        # 1. filter out any point that is not a local maxima over a certain area
        t0 = time.time()
        candidates_with_elevations = self._find_local_maxima()
        t1 = time.time()

        print "Number after _find_local_maxima: {}".format(len(
                                                    candidates_with_elevations))
        print "TIME _find_local_maxima: {}".format(t1 - t0)
 
        # 2. filter remaining candidates by checking if there are obstructions 
        # to the west
        t0 = time.time()
        candidates_with_elevations = [candidate for candidate
                                      in candidates_with_elevations 
                                      if self._is_unobstructed_west(candidate)]
        t1 = time.time()

        print "TIME _is_unobstructed_west: {}".format(t1 - t0)

        print "Num candidates after obstruction filtering = {}".format(
            len(candidates_with_elevations))


        # Find the elevation of the point that the user entered
        self._elevation_of_center = self._elevation_by_indices(
                                        self._user_latlong_coordinates)

        # Create a new list to store all candidate points indices and a list of
        # their corresponding scores. Will be in the form:
        # [((row_index, column_index), [elevation_score, cliff_score]), ...]
        candidates_with_all_scores = []

        # Add elevation score and cliff score to candidate_point tuple
        t0 = time.time()
        for candidate_point in candidates_with_elevations:
            # Elevation of the candidtate point
            candidate_elevation = candidate_point[1]
            # The elevation score is the elevation at the candidate point minus 
            # The elevation of the starting point
            elevation_score = candidate_elevation - self._elevation_of_center
            # Get the cliff score for the candidate point
            cliff_score = self._get_cliff_score(candidate_point)
            
            # Append the scores to the candidates list
            candidates_with_all_scores.append((candidate_point[0], 
                [elevation_score, cliff_score]))

        t1 = time.time()
        print "TIME _get_cliff_score and elevation_score: {}".format(t1 - t0)
        
        # Rank and sort points based on ranking - rank function only returns 
        # the top 100
        t0 = time.time()
        ranked_points = self._rank_candidate_points(candidates_with_all_scores)
        t1 = time.time()

        print "TIME _rank_candidate_points: {}".format(t1 - t0)
        print "First 100 candidate points sorted by rank"
        print ranked_points

        # Create a new list of just latlongs
        final_latlongs = []

        t0 = time.time()
        # Finally, convert these top 100 points to latlongs
        for final_point in ranked_points[:self._number_of_points_returned]:
    
            final_latlongs.append(self._convert_to_latlong(final_point[0]))

        t1 = time.time()
        print "TIME _convert_to_latlong: {}".format(t1 - t0)

        print "NUMBER OF FINAL LATLONGS {}".format(len(final_latlongs))

        return final_latlongs

    def _create_elevation_array(self):
        """Create an elevation array containing the data in the .img files 
        surrounding the given latlong.

        The array will be constructed from the dictionary of filenames with the 
        keys in the following structure:

        [NW][N][NE]
         [W][C][E]
        [SW][S][SE]

        The .img files have an overlap of approx. 11.999999880419653 indices. To 
        reconcile this, slice the OVERLAPPING_INDICES off the south and east 
        bounds.

        Will return an array with dimensions of 10,800 * 10,800
        """

        # Create filename dict where the keys correspond to the location that 
        # the file will be in the elevation array
        filename_dict = self._generate_surrounding_filenames()

        # Initiaize a new dictionary that will have the same keys as the 
        # filenams_dict but with the filename read as an arrays as the value
        data_dict = {}

        for file_key in filename_dict:

            # TODO: default img file root to attribute or move file functions 
            # to utilites.py
            # create filepath for each filename
            # filepath = DEFAULT_IMG_FILE_ROOT + filename_dict[file_key]
            filepath = create_filepath(filename_dict[file_key])
            
            try:
                response = app.client.get_object(Bucket='sunsetfunset', Key=filename)
                array = np.load(BytesIO(response['Body'].read()))
                print "ARRAY: {}".format(array)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    exists = False
                    print "got here"
                else:
                    print e
                    raise e
                    print "created look_alike with zeros"
                    look_alike = SunsetViewFinder._read_img_file(
                    "/Users/Sarah/PROJECT/imgfiles/n33w117.img")

                    data_dict[file_key] = np.zeros_like(
                        look_alike)[:-OVERLAPPING_INDICES,:-OVERLAPPING_INDICES]

            # Check to make sure the file exists
            # if os.path.isfile(filepath): 
            #     # Add the array to the dictionary and crop by 12
            #     # on right and bottom
            #     data_dict[file_key] = SunsetViewFinder._read_img_file(
            #         filepath)[:-OVERLAPPING_INDICES,:-OVERLAPPING_INDICES]


            # else:
                # TODO: actually fix this hardcode dimensions and use np.zeros() 
                # xhere
                # Make array of all zeros if file doesn't exist
                # Using an array from a file I know exists to know what 
                # dimensions are
                # look_alike = SunsetViewFinder._read_img_file(
                    # "/Users/Sarah/PROJECT/imgfiles/n33w117.img") # TODO: move 
                # n33w117.img to a constant

                # Use this array to make a look alike - will have same 
                # dimensions with all zeros
                # data_dict[file_key] = np.zeros_like(
                #     look_alike)[:-OVERLAPPING_INDICES,:-OVERLAPPING_INDICES] 
                    
        # Use scipy stacking to vertically concatenate 3 rows that are each 
        # horizontally concatenated over 3 columns
        return (scipy.vstack((
               scipy.hstack((data_dict["NW"], data_dict["N"], data_dict["NE"])),
               scipy.hstack((data_dict["W"], data_dict["C"], data_dict["E"])),
               scipy.hstack((data_dict["SW"], data_dict["S"], data_dict["SE"]))
               )))

    def _new_argrelmax(self, order=BOUNDING_BOX, mode="clip"):
        """Find local maximums over a certain area (the order).

        Argrelmax is a function available in the scipy.signal library that 
        finds local maximums in a 2D numpy array over one axis. This function 
        is influenced by the source code of argrelmax and is customized in 
        order to find local maximums over 2 axes. See the argrelmax source code 
        here:
        https://github.com/scipy/scipy/blob/master/scipy/signal/_peak_finding.py

        Axis 0 refers to the rows, axis 1 refers to the columns. The mode is how
        the function will handle indices that are out of range for the array. 
        The default value "clip" means that it will clip the end if the index
        is out of range. 

        Returns the indies of the local maxima within the array.
        """

        data = self._cropped_elevation_array

        # Creates a numpy array from 0 to the length of the axis in question
        # (aka array of indices the length of the cropped array)
        locs_axis_0 = np.arange(0, data.shape[0])
        locs_axis_1 = np.arange(0, data.shape[1])

        # Creates a numpy 2D array of ones the size of the original data and 
        # with boolean type. All results are true to begin with.
        results = np.ones(data.shape, dtype=bool)
        # Create a main array for each axis by indexing with locs_axis
        # data.take does the same thing as "fancy" indexing (aka use array to 
        # index array)
        main_axis_0 = data.take(locs_axis_0, axis=0, mode=mode)
        main_axis_1 = data.take(locs_axis_1, axis=1, mode=mode)

        # The first loop will look at the rows only (axis 0)
        # Unlike range, xrange is a generator which means it doesn't actually 
        # create or store the list to iterate over. This loop goes through all 
        # the offsets and assigns a boolean value. For example, when shift = 1, 
        # the main axis is compared to the plus and minus axis (which are of
        # of length 1 and shifted over right and left). So essentially every 
        # index in the array is compared to 1 value to the right and left. When
        # shift = 2, the index is compared to two values to the left and two to
        # the left. Will continue to look to the right and left for every shift 
        # up to bounding box.
        for shift in xrange(1, order + 1):
            # Create 2 arrays, one shifted to the right and one to the left
            # by shift index
            plus_axis_0 = data.take(locs_axis_0 + shift, axis=0, mode=mode)
            minus_axis_0 = data.take(locs_axis_0 - shift, axis=0, mode=mode)

            # Compares 2 matrices with a binary operator, if either are false 
            # the result will be false. 
            # The comparator np.greater checks to see if the main axis is 
            # greater than the plus or minus axis and if so the result will be
            # true. 
            results &= np.greater(main_axis_0, plus_axis_0)
            results &= np.greater(main_axis_0, minus_axis_0)
            # if nothing is true, return
            if(~results.any()):
                break

        # The second loop will look at the columns (axis 1)
        # Unlike the first loop, the results array does not start with initial 
        # values of true. Instead, the results array is the result from the 
        # first for loop of looking at the rows.
        for shift in xrange(1, order + 1):
            plus_axis_1 = data.take(locs_axis_1 + shift, axis=1, mode=mode)
            minus_axis_1 = data.take(locs_axis_1 - shift, axis=1, mode=mode)
            
            results &= np.greater(main_axis_1, plus_axis_1)
            results &= np.greater(main_axis_1, minus_axis_1)

        # np.where finds all the points that are true aka the local maximums

        return np.where(results)


    def _find_local_maxima(self):
        """Find local maxima of 2D array and return positions in array.

        The format of the returned coordinates:
         (array([row1, row2]), (array[column1, column2]). 

        For every point returned by argrelmax, check if local maxima condition 
        still true when looking at an area of about FIXME BOUNDING_BOX

        The function returns all local maximums in a list in the form:
        [((row, column), relative_elevation), ... ]

        Elevation relative to starting point.
        """

        t0 = time.time()
        # local_maxima = scipy.signal.argrelmax(self._cropped_elevation_array, 
        #                                       1, 100)
        local_maxima = self._new_argrelmax()

        t1 = time.time()

        print "TIME BREAKDOWN _local_maxima: argrelmax {}".format(t1 - t0)

        print "Num local_maxima from scipy = {}".format(len(local_maxima[0]))

        candidates_with_elevations = []

        t0 = time.time()
        # Loop over every point returned in argrelmax and do further analysis:
        for i in xrange(len(local_maxima[0])):

            # For each local max indices given, find the corresponding elevation
            elevation = self._elevation_by_indices((local_maxima[0][i],
                local_maxima[1][i]))

            # Throw out all negative elevations they are not good for watching 
            # sunsets :)
            # Check each candidate local maxima to see if it is also a maxima 
            # for the area around it. If these conditions are met, append it to 
            # the list of coordinates with elevations.
            if elevation > 0 and self._is_local_maximum((local_maxima[0][i], 
                                    local_maxima[1][i])):
                # Difference between user's entered location and the points 
                # elevation
                # relative_elevation = elevation - elevation_of_center
                candidates_with_elevations.append(((local_maxima[0][i], 
                                                    local_maxima[1][i]), 
                                                    elevation))

        t1 = time.time()
        print "TIME BREAKDOWN _local_maxima: check BOUNDING_BOX {}".format(t1 
                                                                        - t0)

        return candidates_with_elevations

    def _is_unobstructed_west(self, candidate_point):
        """Check that there are no obstructions to the west given an index

        Candidate_point is in the form ((row, column), elevation).
        """
        # check this to make sure it's doing what I want
        
        # tesing rows...see global variable
        row_index_constant = candidate_point[0][0]
        candidate_point_elevation = candidate_point[1]

        row_to_start_obs_check = max(-ROWS_CHECK_OBS_WEST + row_index_constant, 
                                    0)
        row_to_end_obs_check = min(row_index_constant + ROWS_CHECK_OBS_WEST, 
                                   len(self._cropped_elevation_array))

        # TODO: comment this, change any candidate_point reference to variable 
        # name for clarity
        # look 100 indices to the left of candidate point
        for row_index in range(row_to_start_obs_check, row_to_end_obs_check):
            for column_index in range(max(-COLUMNS_CHECK_OBS_WEST + 
                candidate_point[0][1], 0), candidate_point[0][1]):
                
                # print cropped_elevation_array[column_index,row_index_constant]
                
                # check to see if any of the points are higher than the 
                # candidate point
                if (self._cropped_elevation_array[row_index, column_index] > 
                    candidate_point_elevation):

                    return False

        return True

    def _get_cliff_score(self, candidate_point):
        """Check to see if there is a dropoff west of the candidate_point

        The score returned will be the ratio of candidate point to the average 
        of the other points. 
        Candidate_point is in the form ((row, column), elevation).
        """

        # Check a few columns next to point to see if the point is a "cliff", 
        # add cliff score to the scores list

        # Unlike is_candidate_local_maxima, this box only goes as far east as 
        # the candidate point
        # TODO: name all the candidate point indexing to make it more readable
        rows_lower_bound = max(-ROWS_FOR_DROPOFF + candidate_point[0][0], 0)
        rows_upper_bound = min(candidate_point[0][0] + ROWS_FOR_DROPOFF, 
                               len(self._cropped_elevation_array))
        column_lower_bound = max(-COLUMNS_FOR_DROPOFF + candidate_point[0][1], 
                                 0)
        column_upper_bound = candidate_point[0][1]


        # print "CANDIDATE POINT"
        # print candidate_point
        candidate_elevation = candidate_point[1] 

        total_points = 0
        other_elevation_total = 0

        for row in range(rows_lower_bound, rows_upper_bound):
            for column in range(column_lower_bound, column_upper_bound):

                total_points += 1

                other_elevation_total += self._cropped_elevation_array[row, 
                                                                       column]

        if total_points == 0:
            cliff_score = 0
        else:
            # Take the average of the checked region
            average_elevation_other = other_elevation_total / total_points

            # If the average elevation is less than add the difference as the 
            # cliff_score
            # if average_elevation_other < candidate_elevation:
            
            # try cliffness proportional to absolute elevation- divide by 
            # candidate_point[1]
            cliff_score = (candidate_elevation - average_elevation_other)


        return cliff_score

    def _convert_to_latlong(self, coordinate):
        """Given a tuple of indicess for a point in the form (row, column), 
        calculate the latlong of that point.

        Using the exact coordinates of the west and north bounds from the db, 
        the latlong is calculated based on the offset from the cropped elevation
        array.
        """

        OFFSET = self._cropped_array_top_left_indices

        # row of coordinate plus row of offset
        elevation_array_row_index = OFFSET[0] + coordinate[0]
        elevation_array_column_index = OFFSET[1] + coordinate[1]

        lat_final = (self._nbound - elevation_array_row_index * 
                        DEGREES_PER_INDEX)
        long_final = (self._wbound + elevation_array_column_index * 
                        DEGREES_PER_INDEX)
        # elevation_array_w_bound should be negative here
        # add because it will be greater to the right

        #print "FINAL COORDINATES:"
        #print (lat_final, long_final)

        return (lat_final, long_final)

    def _generate_surrounding_filenames(self):
        """Generate dictionary of filenames for the surrounding data for a given 
        latlong.

        The key of the dictionary represents where that tile is located in terms
        of the center tile (the tile that contains the original latlong).
        """

        n, w = get_filename_n_w(self._latlong)

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

    def _crop_elevation_array(self):
        """Crop the elevation_data_array to approximately a 20 mile radius (1073
        entries: each index represents approximately .0186411357696567 miles)
        around the given latlong.

        The latlong the user entered will be the center of the radius. The 
        values of the 2D array within the radius will remain their original 
        value and the values outside of the radius will be changed to -1000, an 
        arbitrary low number. This is done using a mask. An array just outside 
        this radius will be returned along with the NW (top left) coordinate of 
        the new array. The radius array dimensions will be 2146 x 2146.
        """
      
        # Coordinates for user entered point in terms of master array
        y_index, x_index = self._find_coordinates()

        # n = len(elevation_array)

        # Creating the box around the radius by setting a beginning and ending 
        # point
        y_begin = max(y_index - self._radius_in_indices, 0)
        y_end = y_index + self._radius_in_indices + 1
        x_begin = max(x_index - self._radius_in_indices, 0)
        x_end = x_index + self._radius_in_indices + 1
       
        cropped_elevation_array = self._elevation_array[y_begin:y_end, 
                                                        x_begin:x_end]

        cropped_array_top_left_indices = (y_begin, x_begin)

        # Find the postion of the user's latlong by offesetting the cropped 
        # array
        user_latlong_coordinates_cropped = (y_index - y_begin, x_index - 
                                                x_begin)

        return (cropped_elevation_array, cropped_array_top_left_indices, 
                    user_latlong_coordinates_cropped)

    def _elevation_by_indices(self, coordinates):
        """Search the cropped_elevation_array by coordinates and return the 
        elevation at that point.

        [row, column]
        """

        elevation = self._cropped_elevation_array[coordinates[0], 
                        coordinates[1]]

        return elevation

    def _is_local_maximum(self, candidate_point):
        """Check to see if realative maximum is realative max over an area of 
        TODO: finish this docstring

        10 indices for now
        """

        rows_lower_bound = max(-(BOUNDING_BOX) + candidate_point[0], 0)
        rows_upper_bound = min(candidate_point[0] + (BOUNDING_BOX), 
                               len(self._cropped_elevation_array))
        column_lower_bound = max(-(BOUNDING_BOX) + candidate_point[1], 0)
        column_upper_bound = min(candidate_point[1] + (BOUNDING_BOX), 
                                 len(self._cropped_elevation_array))

        # maybe change the following by passing the elevation with the candidate
        # point?
        candidate_elevation = self._elevation_by_indices(candidate_point) 

        # TODO: comment and doc string
        for row in range(rows_lower_bound, rows_upper_bound):
            for column in range(column_lower_bound, column_upper_bound):

                # If the elevation of a point is greater than the elevation for 
                # the candidate point, return False meaning the candidate point 
                # will be thrown out as a local maxima. 
                if (self._cropped_elevation_array[row][column] >
                    candidate_elevation):
                    return False
        
        return True

    def _find_coordinates(self):
        """Find index for elevation array of a given latlong.

        The indices will be calculated with the exact N and W bounds from the 
        database. DEGREES_PER_INDEX is calculated by taking the difference of NS
        (or EW) bounds and dividing 3612 (the length and width of a single 
        file). DEGREES_PER_INDEX is calculated to be 0.0002777777777685509.
        """

        lat = self._latlong[0]
        lng = self._latlong[1]

        # check absolute values 
        y_index = int(round(abs((self._nbound - lat) / DEGREES_PER_INDEX)))
        x_index = int(round(abs((self._wbound - lng) / DEGREES_PER_INDEX)))

        return (y_index, x_index)

    @staticmethod
    def _convert_radius_to_indices(user_radius_miles):
        """Take the mileage that the user inputted and conver to how many
        indices if would represent. 

        Each index represents approximately .0186411357696567 miles
        """
        # TODO: move to constant
        return int(float(user_radius_miles) / MILES_PER_INDEX)

    @staticmethod
    def _rank_candidate_points(candidate_points):
        """Using a candidate point's scores, return a ranking for how good of a
        sunset viewing spot the point is. Returns the top 100 ranked sunsets.

        Returns a list of tuples of coordinates with the indices and the 
        calculated ranking. The list is sorted by ranking.
        """

        candidates_with_ranking = []
        candidates_score = 0

        for candidate_point in candidate_points:
            # print "HERE I AM"
            # print candidate_point

            elevation_score = candidate_point[1][0]
            cliffiness_score = candidate_point[1][1]

            # Multiply the scores by weight to create a ranking number
            candidates_score = (elevation_score * .05) + (cliffiness_score * .1)
            # candidates_score = elevation_score * cliffiness_score

            # Add point and rank to a list
            candidates_with_ranking.append((candidate_point[0], 
                                            candidates_score))

        # Sort list in descending order by ranking
        candidates_with_ranking.sort(key=itemgetter(1), reverse=True)

        return candidates_with_ranking[:100]

    @staticmethod
    def _read_img_file(filepath):
        """Read .img file as 2D numpy array given a filepath. 

        The .img files are raster data. The osgeo library provides a way to 
        open these files and read them as a numpy 2D array.

        Each array of 1 arc second should have dimensions 3612 x 3612. 
        """

        geo = gdal.Open(filepath)
       
        arr = geo.ReadAsArray()

        return arr


# test = SunsetViewFinder((36.79, -117.05), 38.00166666667, -118.0016666667, 20)
# print test.pick_best_points()

