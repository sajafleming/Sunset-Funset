import unittest
from find_sunset_spots import *

class SunsetTests(unittest.TestCase):

    def test_generate_surrounding_filenames(self):
        test_latlong = (4.5, -10)
        sunset_view_finder = SunsetViewFinder(test_latlong, 6, 11, 10)
        self.assertEqual(sunset_view_finder._generate_surrounding_filenames(
                            sunset_view_finder._latlong), 
        {'C': 'n5w10.img','E': 'n5w9.img', 'W': 'n5w11.img', 'S': 'n4w10.img', 
         'N': 'n6w10.img', 'SW': 'n4w11.img', 'NE': 'n6w9.img', 
         'SE': 'n4w9.img', 'NW': 'n6w11.img'})

    def test_read_img_file(self):
        testing = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img")
        self.assertEqual(len(testing), 3612)





    

if __name__ == "__main__":
    unittest.main()