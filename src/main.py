import argparse
import json
import os
import sys
import f2n
from parse_fits import parse_fits
from weather_scraper import scraper


parser = argparse.ArgumentParser(description="Handles tasks for the St Andrews observatory web app.")

parser.add_argument('--weather', '-w',
                    nargs=1,
                    help='Weather takes a path at which to dump the latest forecast file.')
parser.add_argument('--fits', '-f',
                    nargs=2,
                    help='Fits takes a [source folder], parses all fits files below it and dumps JSON representations'
                         ' into the [output folder].')
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
    # go through non completed fits files
    for fits_object in fits_parser.index_directory_of_fits_files(args.fits[0], completed)['files']:
        out_stem = os.path.join(args.fits[1], str(fits_object['epoch']))
        # json dump
        with open(out_stem + '.json', 'w') as file:
            json.dump(fits_object, file)
        # convert and dump image
        myimage = f2n.fromfits(fits_object['path'])
        myimage.setzscale()
        myimage.makepilimage('lin')
        myimage.tonet(out_stem + '.png')
        # add path to completed list
        completed.append(str(fits_object['path']))
    with open(completed_path, "w+") as file:
        json.dump(completed, file)
    # refresh index of out dir
    with open(os.path.join(args.fits[1], 'index.json'), 'w') as file:
        json.dump([f.replace('.json', '')
                   for f
                   in os.listdir(args.fits[1]) if f.endswith('json')], file)

if args.weather is not None:
    # check output path is available
    if not os.path.exists(args.weather[0]):
        sys.exit("There's no directory at " + os.path.abspath(args.weather[0]))
    forecaster = scraper()
    forecast = forecaster.summarise_current_forecasts()
    with open(os.path.join(args.weather[0], str(forecast['epoch']) + '.json'), 'w') as file:
        json.dump(forecast, file)

