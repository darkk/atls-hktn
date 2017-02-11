#!/usr/bin/env python2.7

import ujson
import sys

from datadict import *

def main():
    probes = ujson.load(sys.stdin)
    geo24 = dict()
    for p in probes['objects']:
        if p['latitude'] is not None and p['address_v4']:
            geo24[ ip24(p['address_v4']) ] = (p['latitude'], p['longitude'])
    pickle.dump(prbids, sys.stdout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
