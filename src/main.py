import argparse
import json
import os
import sys
import f2n
from parse_fits import parse_fits
from weather_scraper import scraper

# main.py contains the code which parses and handles the command line arguments provided
# it also does some management of the files

parser = argparse.ArgumentParser(description="Handles tasks for the St Andrews observatory web app.")

parser.add_argument('--weather', '-w',
                    nargs=1,
                    help='Weather takes a path at which to dump the latest forecast file.')
parser.add_argument('--fits', '-f',
                    nargs=2,
                    help='Fits takes a [source folder], parses all fits files below it and dumps JSON representations'
                         ' into the [output folder].')
parser.add_argument('--init', '-i',
                    nargs=2,
                    help='initialises data directory, this command will set all source fits files to ignore.')
args = parser.parse_args()

print args

if args.fits is not None:
    # check input path is available
    if not os.path.exists(args.fits[0]):
        sys.exit("There's no directory at " + os.path.abspath(args.fits[0]))
    # check output path is available
    if not os.path.exists(args.fits[1]):
        sys.exit("There's no directory at " + os.path.abspath(args.fits[1]))
    fits_parser = parse_fits()
    # load completed files
    completed_path = os.path.join(args.fits[1], 'completed.json')
    completed = []
    if os.path.exists(completed_path):
        with open(completed_path, "r") as file:
            completed = json.load(file)
    # load ignore folders
    ignore_folders_path = os.path.join(args.fits[1], 'images', 'ignore_folders.json')
    ignore_folders = set()
    if os.path.exists(ignore_folders_path):
        with open(ignore_folders_path, "r") as file:
            ignore_folders = ignore_folders.union(set(json.load(file)))
    # get current folders
    ignore_folders_path = os.path.join(args.fits[1], 'ignore_folders.json')
    source_dirs = set([name for name in os.listdir(args.fits[0]) if os.path.isdir(os.path.join(args.fits[0], name))])
    # and diff with ignored folders
    dirs_to_parse = source_dirs.difference(ignore_folders)
    print dirs_to_parse
    print ignore_folders
    print source_dirs
    # go through new folders
    for dir in dirs_to_parse:
        for fits_object in fits_parser.index_directory_of_fits_files(os.path.join(args.fits[0], dir), completed)['files']:
            out_stem = os.path.join(args.fits[1], 'images', str(fits_object['epoch']))
            # json dump
            with open(out_stem + '.json', 'w') as file:
                json.dump(fits_object, file)
            # convert and dump image
            myimage = f2n.fromfits(fits_object['path'])
            myimage.setzscale()
            myimage.makepilimage('lin')
            print "------"
            myimage.tonet(out_stem + '.png')
            # add path to completed list
            completed.append(str(fits_object['path']))
        with open(completed_path, "w+") as file:
            json.dump(completed, file)
    # refresh index of out dir
    with open(os.path.join(args.fits[1], 'images', 'index.json'), 'w') as file:
        json.dump([f.replace('.json', '')
                   for f
                   in os.listdir(os.path.join(args.fits[1], 'images')) if f.endswith('json') and not f == 'ignore_folders.json' and not f == 'index.json'], file)

if args.init is not None:
    weather = os.path.join(args.init[1], 'weather')
    fits = os.path.join(args.init[1], 'images')
    if not os.path.exists(weather):
        os.makedirs(weather)
    if not os.path.exists(fits):
        os.makedirs(fits)
    # check if there is an ignore folder section
    ignore_folders = os.path.join(fits, 'ignore_folders.json')
    source_dirs = [name for name in os.listdir(args.init[0]) if os.path.isdir(os.path.join(args.init[0], name))]
    print source_dirs
    dirs_to_parse = []
    # if there isn't (ie first run) then dump source folders into and ignore folders file
    if not os.path.exists(ignore_folders):
        with open(ignore_folders, 'w') as file:
            json.dump(source_dirs, file)
    else:
        print "It seems like you've already run init script since the ignore list is already set up. Delete it if " \
              "you want to re-init"

if args.weather is not None:
    weather_root = os.path.join(args.weather[0], 'weather')
    # check output path is available
    if not os.path.exists(os.path.join(args.weather[0], 'weather')):
        sys.exit("There's no directory at " + os.path.abspath(args.weather[0]))
    forecaster = scraper()
    forecast = forecaster.summarise_current_forecasts()
    with open(os.path.join(weather_root, str(forecast['epoch']) + '.json'), 'w') as file:
        json.dump(forecast, file)
    # refresh index of out dir
    with open(os.path.join(weather_root, 'index.json'), 'w') as file:
        json.dump([f.replace('.json', '')
                   for f
                   in os.listdir(os.path.join(args.weather[0], 'weather')) if f.endswith('json') and not f == 'index.json'], file)
