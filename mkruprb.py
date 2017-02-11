#!/usr/bin/env python2.7

import ujson
import sys

from datadict import *

def main():
    probes = ujson.load(sys.stdin)

    prbids = set()
    for p in probes['objects']:
        if p['latitude'] is not None:
            if (False
                or p['address_v4'] and v4mask[ip24(p['address_v4'])]
                or p['asn_v4'] in asnset
                or p['country_code'] == 'RU'
            ):
                prbids.add(p['id'])
    pickle.dump(prbids, sys.stdout, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
