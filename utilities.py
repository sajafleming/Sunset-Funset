""" Functions that know how to function """

from math import ceil

def find_filename_n_w(latlong):
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

    return n, w 


def create_filename(n, w):
    """Given integer n and w coordinates, create a filename string"""

    return "n%sw%s.img" % (n, w)

