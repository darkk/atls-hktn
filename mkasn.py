#!/usr/bin/env python2.7

from bitarray import bitarray
from netaddr import IPNetwork
import cPickle as pickle
import sys
import ujson

def main():
    asnset = set()
    res = ujson.load(sys.stdin)
    for asn in res['data']['resources']['asn']:
        asn = int(asn)
        asnset.add(asn)
    pickle.dump(asnset, sys.stdout, pickle.HIGHEST_PROTOCOL)
    print >>sys.stderr, len(asnset), 'AS numbers'

if __name__ == '__main__':
    main()
