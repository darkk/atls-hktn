#!/usr/bin/env python2.7

import cPickle as pickle
import os
import sys
try:
    from netaddr import IPAddress
except ImportError:
    pass

from haversine import haversine

def load(fname):
    if os.path.exists(fname) and os.stat(fname).st_size > 0:
        return pickle.load(open(fname))
    else:
        return None

v4mask = load('24bitarray_20170130.pickle') # RU IPv4 int24 (bitset)
asnset = load('asn_20170130.pickle')        # RU asn (set)
prbids = load('prbids_20170130.pickle')     # RU prbid (set)
geo24 = load('geo24_20170130.pickle')       # WW int24 -> lat, lon (dict)
geoprb = load('geoprb_20170130.pickle')     # WW prbid -> lat, lon (dict)

SOL = 0.69 * 299.792458 / 2 # RTT km/ms, 0.69 factor for fiber https://habrahabr.ru/post/174225/

del load

def ip24(s):
    return (int(IPAddress(s)) >> 8)
