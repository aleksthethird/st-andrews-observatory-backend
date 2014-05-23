import argparse
import json
import os
import sys
import f2n
from parse_fits import parse_fits


parser = argparse.ArgumentParser(description="Handles tasks for the St Andrews observatory web app.")

parser.add_argument('--weather', '-w',
                    nargs=1,
                    help='Weather takes a path at which to dump the latest forecast file.')
parser.add_argument('--fits', '-f',
                    nargs=2,
                    help='Fits takes a [source folder], parses all fits files below it and dumps JSON representations'
                         ' into the [output folder].')
args = parser.parse_args()
