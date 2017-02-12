#!/usr/bin/env python2.7

import sys
from math import isinf
from contextlib import closing
from cStringIO import StringIO
from subprocess import Popen, PIPE

import ujson
try:
    import lz4.frame as lz4f
except ImportError:
    print >>sys.stderr, 'Get python-lz4 from master -- https://github.com/python-lz4/python-lz4/'
    raise

from datadict import *

# traceroute - msm/7740605-1485516655-1485603055.json.lz4
# ping - msm/1005016.json.lz4

class LZ4Pipe(object):
    def __init__(self, fname):
        self.proc = Popen(['lz4cat', fname], stdin=open(fname, 'rb'), stdout=PIPE)
    def __iter__(self):
        return iter(self.proc.stdout)
    def close(self):
        try:
            self.proc.kill()
        except Exception:
            pass
        self.proc.wait()

def openpipe(fname):
    if os.stat(fname).st_size < 1024*1024:
        with open(fname, 'rb') as fd:
            blob = fd.read()
        try:
            blob = lz4f.decompress(blob)
            return StringIO(blob)
        except RuntimeError:
            return LZ4Pipe(fname)
    else:
        return LZ4Pipe(fname)

def ruler(fname):
    with closing(openpipe(fname)) as fd:
        for msm in fd:
            msm = ujson.loads(msm)
            srcll = geoprb[msm['prb_id']] # lat/lon
            dstll = geo24[ip24(msm['dst_addr'])]
            if msm['type'] == 'ping':
                first, rtt = float('nan'), msm['min']
            elif msm['type'] == 'traceroute':
                first, rtt = float('inf'), float('inf')
                for rhop in msm['result'][-2:]:
                    for rres in rhop.get('result', ()):
                        if rres.get('from') == msm['dst_addr'] and rres.get('rtt', float('inf')) < rtt:
                            rtt = rres.get('rtt', float('inf'))
                if isinf(rtt):
                    continue # useless measurement

                for rres in msm['result'][0]['result']:
                    if rres.get('rtt', float('inf')) < first:
                        first = rres.get('rtt', float('inf'))
                if isinf(first):
                    first = float('nan')
            else:
                raise RuntimeError('WTF?', msm['type'])
            print msm['msm_id'], msm['prb_id'], msm['from'], srcll[0], srcll[1], msm['dst_addr'], dstll[0], dstll[1], haversine(srcll, dstll) / SOL, rtt, first

def main():
    for fname in sys.argv[1:]:
        ruler(fname)

if __name__ == '__main__':
    main()
