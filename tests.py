import unittest
from find_sunset_spots import *

NW = [ [0 1 2],
       [3 4 5],
       [6 7 8], ]
NE = [ [0 1 2],
       [3 4 5],
       [6 7 8] ]
SW = [ [0 1 2],
       [3 4 5],
       [6 7 8] ]
SE = [ [0 1 2],
       [3 4 5],
       [6 7 8] ]
N = [  [0 1 2],
       [3 4 5],
       [6 7 8] ]
S = [  [0 1 2],
       [3 4 5],
       [6 7 8] ]
E = [  [0 1 2],
       [3 4 5],
       [6 7 8] ]
W = [  [0 1 2],
       [3 4 5],
       [6 7 8] ]


class SunsetTests(unittest.TestCase):

    def test_generate_surrounding_filenames(self):
        test_latlong = (4.5, -10)
        sunset_view_finder = SunsetViewFinder(test_latlong, 6, 11, 10)
        self.assertEqual(sunset_view_finder._generate_surrounding_filenames(
                            sunset_view_finder._latlong), 
        {'C': 'n5w10.img','E': 'n5w9.img', 'W': 'n5w11.img', 'S': 'n4w10.img', 
         'N': 'n6w10.img', 'SW': 'n4w11.img', 'NE': 'n6w9.img', 
         'SE': 'n4w9.img', 'NW': 'n6w11.img'})

    def get_tiles_needed(self):
        






    

if __name__ == "__main__":
    unittest.main()