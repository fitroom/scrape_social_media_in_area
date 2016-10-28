#!/usr/bin/env python

# Gets data from the Foursquare API in a given region. Notably, that's the
# businesses, not the user checkins.

import argparse, random, ConfigParser, os, time, datetime, traceback, json
import psycopg2, psycopg2.extensions, psycopg2.extras, time, utils 
import requests, numpy as np

config = ConfigParser.ConfigParser()
config.read('config.txt')

OAUTH_KEYS = [{'client_id': config.get('foursquare-' + str(i), 'client_id'),
              'client_secret': config.get('foursquare-' + str(i), 'client_secret')}
             for i in range(int(config.get('num_foursquare_credentials', 'num')))]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required=True, choices=utils.CITY_LOCATIONS.keys())
    parser.add_argument('--output_file', default='4sq_venues.json')
    parser.add_argument('--granularity', type=float, default=.005)
    args = parser.parse_args()

    # psql_conn = psycopg2.connect("dbname='tweet'")

    city_min_lon, city_min_lat, city_max_lon, city_max_lat =\
            [float(s.strip()) for s in \
            utils.CITY_LOCATIONS[args.city]['locations'].split(',')]
    SEARCH_URL = 'https://api.foursquare.com/v2/venues/search'
    OAUTH_KEYS = [{'client_id': config.get('foursquare-' + str(i), 'client_id'),
            'client_secret': config.get('foursquare-' + str(i), 'client_secret')}
            for i in range(int(config.get('num_foursquare_credentials', 'num')))]
    OAUTH_KEY = OAUTH_KEYS[0] # TODO change this if we want > 1 4sq credential.

    venues = []

    for lat in np.arange(city_min_lat, city_max_lat, args.granularity):
        for lon in np.arange(city_min_lon, city_max_lon, args.granularity):
            sw = '%s,%s' % (lat, lon)
            ne = '%s,%s' % (lat + args.granularity, lon + args.granularity)
            params = {'intent': 'browse', 'sw': sw, 'ne': ne, 'limit': 50,
                    'client_id': OAUTH_KEY['client_id'],
                    'client_secret': OAUTH_KEY['client_secret'],
                    'v': '20161027'} # v = version
            res = requests.get(SEARCH_URL, params=params)
            num_venues = len(res.json()['response']['venues'])
            print sw, ne, num_venues
            if num_venues == 50:
                print "Maxed out with 50 venues returned: ", sw, ne
            venues.extend(res.json()['response']['venues'])

            time.sleep(random.randint(1, 10))
    json.dump(venues, open(args.output_file, 'w'), indent=2)

