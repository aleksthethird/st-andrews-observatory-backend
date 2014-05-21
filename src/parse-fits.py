import unittest
from astropy.io import fits
import scipy


class parse_fits:

    def __init__(self):
        pass

    def get_meta(self, path):
        """
        parses fits file header into dictionary
        """
        fits_file = fits.open(path)
        obj = {
            path: {
                x: {
                    'data': y,
                    'comment': z
                }
                for (x, y, z)
                in fits_file[0].header.cards
            }
        }
        fits_file.close()
        return obj


class ParseFistTest(unittest.TestCase):
    def setUp(self):
        self.parser = parse_fits()
        self.fits_test_file = "../test-files/test.fits"

    def test_parse_meta(self):
        self.parser.get_meta(self.fits_test_file)



