#!/usr/bin/env python2.7

import ujson
import sys

from datadict import *

def main():
    probes = ujson.load(sys.stdin)
    geo24 = dict()
    for p in probes['objects']:
        if p['latitude'] is not None and p['address_v4']:
            net = ip24(p['address_v4'])
            if net not in geo24:
                geo24[net] = (p['latitude'], p['longitude'])
            else:
                distance = haversine(geo24[net], (p['latitude'], p['longitude']))
                if distance > 15:
                    print >>sys.stderr, 'Dropped', p['address_v4'], distance, geo24[net], '->', p['latitude'], p['longitude']
                    del geo24[net]
                # FIXME: else -- calc average
    print >>sys.stderr, len(geo24), 'geocoded /24'
    pickle.dump(geo24, sys.stdout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
