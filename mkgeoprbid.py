#!/usr/bin/env python2.7

import ujson
import sys

from datadict import *

def main():
    probes = ujson.load(sys.stdin)
    geo24 = dict()
    for p in probes['objects']:
        if p['latitude'] is not None:
            geo24[ p['id']  ] = (p['latitude'], p['longitude'])
    print >>sys.stderr, len(geo24), 'geocoded probe IDs'
    pickle.dump(geo24, sys.stdout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
