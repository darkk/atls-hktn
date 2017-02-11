#!/usr/bin/env python2.7

import cPickle as pickle
import os
from netaddr import IPAddress

def load(fname):
    if os.path.exists(fname) and os.stat(fname).st_size > 0:
        return pickle.load(open(fname))
    else:
        return None

v4mask = load('24bitarray_20170130.pickle')
asnset = load('asn_20170130.pickle')
prbids = load('prbids_20170130.pickle')

del load

def ip24(s):
    return (int(IPAddress('1.2.3.4')) >> 8)
