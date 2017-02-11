#!/usr/bin/env python2.7

import ujson
import sys

from datadict import *

def main():
    for doc in sys.stdin:
        doc = ujson.loads(doc) # NB: trailing whitespace is not a big deal for `ujson`
        if doc['type']['name'] in ('ping', 'traceroute'):
            for p in doc['probes']:
                if p['id'] in geoprb:
                    srclat, srclon = geoprb[p['id']]
                    dstlat, dstlon = geo24[ip24(doc['dst_addr'])]
                    print doc['msm_id'], p['id'], srclat, srclon, dstlat, dstlon

if __name__ == '__main__':
    main()
