from collections import Counter
from itertools import count
import json
import urllib2
import unittest
from lxml import etree
import feedparser
import time
import xmltodict


class scraper:
    """
    This class is used to scrape weather from various sources and dump the data as json files
    """

    def __init__(self):
        with open('meta/keys.json', 'r') as file:
            self.keys = json.load(file)
        self.constants = {}
        self.constants['bbc_3day'] = "http://open.live.bbc.co.uk/weather/feeds/en/2638864/3dayforecast.rss"
        self.constants['bbc_observations'] = "http://open.live.bbc.co.uk/weather/feeds/en/2638864/observations.rss"
        self.constants['met_3hour'] = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/353305?res=3hou" \
                                      "rly&key=" + self.keys['met']
        self.constants['met_3hour_steps'] = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/capabilit' \
                                            'ies?res=3hourly&key=' + self.keys['met']
        self.constants['yr_forecast'] = "http://api.yr.no/weatherapi/locationforecast/1.9/?lat=56.33;lon=-2.81;msl=30"
        self.constants['met_observations'] = "http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/3171?res" \
                                             "s=hourly&key=" + self.keys['met']
        with open('meta/met-codes.json', 'r') as file:
            self.constants['met_codes'] = json.load(file)

    def get_raw(self, url):
        """
        gets raw http response from url
        """
        print url
        feed = urllib2.urlopen(url)
        raw = feed.read()
        return raw.decode('utf-8')

    def get_xml_path(self, xml, path):
        """
        gets xpath from xml string
        """
        tree = etree.parse(xml)
        return tree.xpath()

    def get_feed(self, url):
        """
        parses an RRS feed using feedpasser
        """
        return feedparser.parse(url)


    def get_yr_forecast(self):
        """
        downloads yr forecast in xml and returns it as a JSON object
        """
        xml = self.get_raw(self.constants['yr_forecast'])
        return xmltodict.parse(xml)

    def parse_time(self, time_string):
        """
        parses the time format below
        """
        pattern = '%Y-%m-%dT%H:%M:%SZ'
        return int(time.mktime(time.strptime(time_string, pattern)))

    def convert_bearing_to_letters(self, angle):
        """
        Takes a bearing ie 180 and converts it to a simple ie S
        """
        bearings = ['NEN','NE','NEE','E','SEE','SE','SES','S','SWS','SW','SWW','W','NWW','NW','NWN']
        sta = 11.25
        ste = 22.5
        nex = sta + ste
        for b in bearings:
            if sta <= angle < nex :
                return b
            nex = nex + ste
        if 0 <= angle < sta or 360-ste <= angle <= 360:
            return 'N'

    def formatted_yr_forecast(self):
        """
        returns a json object which is a bit more friendly to read and also is as consistent as possible
        with other sources
        """
        forecast_object = self.get_yr_forecast()
        formatted = [
            {
                'time': self.parse_time(x['@from']),
                'cloud': {
                    'cover': x['location']['cloudiness']['@percent'],
                    'high-cover': x['location']['highClouds']['@percent'],
                    'low-cover': x['location']['lowClouds']['@percent'],
                    'med-cover': x['location']['mediumClouds']['@percent'],
                    'fog': x['location']['mediumClouds']['@percent']
                },
                'pressure': x['location']['pressure']['@value'],
                'wind': {
                    'direction': self.convert_bearing_to_letters(x['location']['windDirection']['@deg']),
                    'speed': x['location']['windSpeed']['@mps']
                },
                'humidity': x['location']['humidity']['@value']
            }
            for x
            in forecast_object['weatherdata']['product']['time']
            if len(x['location']) is 14
        ]
        return formatted

    def get_met_forecast(self):
        """
        loads up and does some basic parsing of the met forecast feed
        """
        met_raw = self.get_raw(self.constants['met_3hour'])
        met_unnested = []
        for x in json.loads(met_raw)['SiteRep']['DV']['Location']['Period']:
            met_unnested += x['Rep']
        return met_unnested

    def translate_met_code(self, code):
        """
        translates met codes into strings based on lookup table
        """
        return self.constants['met_codes']['codes'][code]

    def get_met_data_steps(self):
        """
        loads the time intervals at which the met forecasts are made
        """
        steps = json.loads(self.get_raw(self.constants['met_3hour_steps']))
        return [self.parse_time(x) for x in steps['Resource']['TimeSteps']['TS']]

    def formatted_met_forecast(self):
        """
        returns a json object which is a bit more friendly to read and also is as consistent as possible
        with other sources
        """
        forecast_object = self.get_met_forecast()
        steps = iter(self.get_met_data_steps())
        formatted = [
            {
                'time': steps.next(),
                'cloud': self.translate_met_code(x['W']),
                'wind': {
                    'direction': x['D'],
                    'speed': x['S']
                },
                'humidity': x['H']
            }
            for x
            in forecast_object
        ]
        return formatted

    def summarise_current_forecasts(self):
        return {
            'epoch': time.time(),
            'met': self.formatted_met_forecast(),
            'yr.no': self.formatted_yr_forecast()
        }

    def map_yr_to_met_codes(self):
        pass


class scraper_test(unittest.TestCase):
    def setUp(self):
        self.scraper = scraper()

    def test_bbc_fetch_xml(self):
        assert "" != self.scraper.get_raw(self.scraper.constants['bbc_3day'])

    def test_bbc_fetch_xml_path(self):
        xml = self.scraper.get_raw(self.scraper.constants['bbc_3day'])

    def test_met_fetch_object(self):
        print self.scraper.get_met_forecast()

    def test_yr(self):
        self.scraper.get_yr_forecast()

    def test_yr_format(self):
        self.scraper.formatted_yr_forecast()

    def test_met_format(self):
        print self.scraper.formatted_met_forecast()

    def test_bearings(self):
        Counter([
            self.scraper.convert_bearing_to_letters(x)
            for x
            in range(360)
        ])