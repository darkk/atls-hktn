#!/usr/bin/env python2.7

from bitarray import bitarray
from netaddr import IPNetwork
import cPickle as pickle
import sys
import ujson

def main():
    v4mask = bitarray(2**24)
    v4mask.setall(False)
    res = ujson.load(sys.stdin)
    for v4pfx in res['data']['resources']['ipv4']:
        v4pfx = IPNetwork(v4pfx)
        if v4pfx.prefixlen <= 24:
            v4mask[ int(v4pfx.network)>>8 : 1+(int(v4pfx.broadcast)>>8) ] = True
        else:
            print >>sys.stderr, 'Drop tiny prefix', v4pfx
    pickle.dump(v4mask, sys.stdout, pickle.HIGHEST_PROTOCOL)
    print >>sys.stderr, v4mask.count(True), '/24 prefixes'

if __name__ == '__main__':
    main()
