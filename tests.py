import unittest
from utilities import *

class utilities_tests(unittest.TestCase):

    def test_find_filename(self):
        self.assertEqual(find_filename((38.0016666667, -118.001666667)), ("n39w119.img", 39, 119))

    def test_create_filename(self):
        self.assertEqual(create_filename(33, 117), "n33w117.img")
        self.assertNotEqual(create_filename(33, 117), "n33w117")

    def test_validate_location_for_search(self):
        self.assertTrue(validate_location_for_search((38.0016666667, -118.001666667)), True)
        self.assertFalse(validate_location_for_search((35.8617, 104.1954)), False)

    def test_create_filepath(self):
        self.assertEqual(create_filepath("n36w115.img"), "/Users/Sarah/PROJECT/imgfiles/n36w115.img")

    def test_generate_surrounding_filenames(self):
        self.assertEqual(generate_surrounding_filenames((4.5, -10)), {'C': 'n5w10.img',
         'E': 'n5w9.img', 'W': 'n5w11.img', 'S': 'n4w10.img', 'N': 'n6w10.img', 
         'SW': 'n4w11.img', 'NE': 'n6w9.img', 'SE': 'n4w9.img', 'NW': 'n6w11.img'})

    def test_read_img_file(self):
        testing = read_img_file("/Users/Sarah/PROJECT/imgfiles/n33w117.img")
        self.assertEqual(len(testing), 3612)

    def test_create_elevation_array(self):
        pass

    # def test(self):
    #     # create fake latlon
    #     latlong = ()

    #     # create fake elevation array
    #     test_array = np.arry([1, 1, 4, 1],
    #                          [1, 9, 1, 1], 
    #                          [7, 1, 1, 1])

    #     # create fake other params

    #     highest = (array([1]), array([1]))

    #     self.assertEqual(find_local_maxima(latlong, elevation_array, elevation_array_n_bound, elevation_array_w_bound))
    

if __name__ == "__main__":
    unittest.main()