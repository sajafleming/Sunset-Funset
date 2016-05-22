import unittest
from utilities import *

class utilities_tests(unittest.TestCase):

    def test_find_filename(self):
        self.assertEqual(find_filename((38.0016666667, -118.001666667)), ("n39w119.img", 39, 119))


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