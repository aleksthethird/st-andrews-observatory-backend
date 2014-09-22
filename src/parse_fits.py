import json
import os
import re
import unittest
from astropy.io import fits
import time


class parse_fits:
    """
    This class is used to manage, parse and convert FITS files
    """

    def __init__(self):
        pass

    def parse_fits_date(self, tme, date):
        """
        parses the time format below
        """
        time_string = (date + " " +  tme).split('.')[0]
        pattern = '%Y-%m-%d %H:%M:%S'
        return int(time.mktime(time.strptime(time_string, pattern)))


    def get_meta(self, path):
        """
        parses fits file header into dictionary
        """
        fits_file = fits.open(path)
        obj = {
            'path' : path,
            'headers' : {
                x: {
                    'data': y,
                    'comment': z
                }
                for (x, y, z)
                in fits_file[0].header.cards
            }
        }
        obj['epoch'] = self.parse_fits_date(obj['headers']['UTSTART']['data'], obj['headers']['DATE-OBS']['data'])

        fits_file.close()
        return obj

    def index_directory_of_fits_files(self, root, completed=set()):
        index = {
            'files': []
        }
        for path, dirnames, filenames in os.walk(root):
            rel_path = [os.path.join(path, f) for f in filenames]
            index['files'] += [self.get_meta(file) for file in rel_path
                                if re.match(".fits", os.path.splitext(file)[1])
                                and file not in completed]
        return index

    def dump_index(self, path_in, path_out, completed=set()):
        to_dump = {}
        if len(completed) is not 0:
            with open(path_out, "r") as file:
                to_dump = json.load(file)
        with open(path_out, "w+") as file:
            to_dump.update(self.index_directory_of_fits_files(file))
            json.dump(to_dump)

class ParseFistTest(unittest.TestCase):

    def setUp(self):
        self.parser = parse_fits()
        self.fits_test_file = "../test-files/test.fits"

    def test_parse_meta(self):
        print self.parser.get_meta(self.fits_test_file)

    def test_indexing(self):
        self.parser.index_directory_of_fits_files('../')

    def test_date_parse(self):
        obj = self.parser.get_meta(self.fits_test_file)
        self.assertEqual(1393443746, obj['epoch'])