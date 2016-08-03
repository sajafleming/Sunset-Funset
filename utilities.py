""" Functions that know how to function """

from math import ceil


AWS_IMG_FILE_ROOT = "http://s3.amazonaws.com/sunsetfunset/"
LOCAL_IMG_FILE_ROOT = "/Users/Sarah/PROJECT/imgfiles/"



def get_filename_n_w(latlong):
    """Find the filename of the file that includes data for the given latlong. 
    Return latlong and the n and w integer values in the filename.

    The topographic data is 1-arc-second of resolution and each file has a 
    rounded integer name of the corresponding NW coordinate. Note the exact NESW
    bounds of every tile are stored in a database.

    >>> get_filename_n_w((38.0016666667, -118.001666667))
    (39, 119)
    """

    # The ceiling of the lat coordinate will give the n int value in the filename
    n = int(ceil(latlong[0]))
    # The actually long is negative but the files are named as postitive integers
    # so take the abs value of the coordinate before the ceiling 
    w = int(ceil(abs(latlong[1]))) # will always return a postive integer

    return n, w 


def create_filename(n, w):
    """Given integer n and w coordinates, create a filename string

    >>> create_filename(33, 117)
    'n33w117.img'
    """

    if len(w) == 3:
        return "n%sw%s.img" % (n, w)
    else: 
        return "n" + n + "w" + "0" + w + ".img"


# can use locally or with AWS bucket
def create_filepath(filename, filepath=AWS_IMG_FILE_ROOT):
    """Create filepath for a given .img file"""


    return filepath + filename