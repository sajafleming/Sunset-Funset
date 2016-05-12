"""Populate db with latlong info from txt files"""

from os import listdir
from model import LatLong
from model import connect_to_db, db
from server import app

# Text strings found in all txt files that preceed the exact coordinates
WEST_STRING = "West_Bounding_Coordinate:"
EAST_STRING = "East_Bounding_Coordinate:"
NORTH_STRING = "North_Bounding_Coordinate:"
SOUTH_STRING = "South_Bounding_Coordinate:"
# files ends with _1_meta.txt
TXT_END_CHARACTERS = -11

def get_coordinates_from_txt(filepath):
    """Opens contents of file path as a string, calculates offset and returns
    a splice string for exact NSEW coordinates

    Use this function to find exact coordinates corresponding to each img file."""

    content = open(filepath).read()

    # offset starts from the index of text constant and adds the length of the 
    # text constant string 
    w_offset = calculate_offset(content, WEST_STRING)
    e_offset = calculate_offset(content, EAST_STRING)
    n_offset = calculate_offset(content, NORTH_STRING)
    s_offset = calculate_offset(content, SOUTH_STRING)

    w_coordinate = splice_for_coordinates(content, w_offset)
    e_coordinate = splice_for_coordinates(content, e_offset)
    n_coordinate = splice_for_coordinates(content, n_offset)
    s_coordinate = splice_for_coordinates(content, s_offset)

    return w_coordinate, e_coordinate, n_coordinate, s_coordinate

def calculate_offset(content, direction_string):
    """Calculates offset for descriptive string for a given direction (NSEW)"""

    return content.find(direction_string) + len(direction_string)

def splice_for_coordinates(content, offset):
    """Takes content and offset and splices for the latlong string, will 
    return a float"""

    # slice - start after offset and split on white space
    return float(content[offset:].split()[0])

def files_to_db(path_with_txt_files):
    """Iterate through all txt files, get exact coordinates and add to db"""

    list_of_txt_files = listdir(path_with_txt_files)
    
    for item in list_of_txt_files:
        if item.endswith(".txt"):
            name = item[:TXT_END_CHARACTERS] 
            path = "/Users/Sarah/PROJECT/txtfiles/" + item

            coordinates = get_coordinates_from_txt(path)

            latlong = LatLong(filename=name,
                              w_bound=coordinates[0],
                              e_bound=coordinates[1],
                              n_bound=coordinates[2],
                              s_bound=coordinates[3])
            
            # Add to the session or it won't ever be stored
            db.session.add(latlong)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case table hasn't been created, create it
    db.create_all()

    files_to_db("/Users/Sarah/PROJECT/txtfiles/")