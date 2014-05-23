import json
import os
import unittest
import glob

class archiver:

    def __init__(self):
        pass


    def dump_dated_object(self, epoch, object, out_root):
        out_file_path = os.path.join(out_root, str(epoch) + '.json')
        while os.path.exists(out_file_path):
            out_file_path += ".d"
        with open(out_file_path, "w+") as file:
            json.dump(object, file)

    def index_files(self, root):
        return glob.glob(os.path.join(root, '*.json*'))


class test_archiver(unittest.TestCase):

    def setUp(self):
        self.arch = archiver()

    def test_dump_dated_object(self):
        test = {}
        self.arch.dump_dated_object(123456789, test, "../out")
        self.assertTrue(os.path.exists("../out/123456789.json"))

    def test_index(self):
        self.assertGreater(len(self.arch.index_files('../out')['files']), 0)
