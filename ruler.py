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

# badly geocoded destinations...
baddst = (
    # https://atlas.ripe.net/probes/27782/#!tab-network -- 194.122.76.254
    # https://atlas.ripe.net/probes/6254/#!tab-network -- 194.122.76.250
    # -- same /24, 350 km away -- let's filter that in mkgeo24 :-)
    ip24('194.122.76.250'),
)

pairs = {
    # (i24 << 24 + i24) -> count
}

def ruler(fname):
    with closing(openpipe(fname)) as fd:
        skipped = 0

        for msm in fd:
            if skipped > 5000: # what a boring file
                return

            try:
                try:
                    msm = ujson.loads(msm)
                except Exception:
                    print >>sys.stderr, 'Bad json', fname
                    continue


                try:
                    src_addr = msm['from'] if msm.get('from') else msm['src_addr']
                    dst_net = ip24(msm['dst_addr'])
                    pairskey = (ip24(src_addr) << 24) | dst_net
                    srcll = geoprb[msm['prb_id']] # lat/lon
                    dstll = geo24[dst_net]
                except KeyError:
                    continue # msm without dst_addr || geo lost after /24->latlon update

                if pairs.get(pairskey, 0) > 20:
                    skipped += 1
                    continue

                distance = haversine(srcll, dstll) # km

                if msm['type'] == 'ping':
                    first, rtt = float('nan'), msm['min']
                    if msm['min'] == -1:
                        continue # That's "traceroute showing stars"
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

                pairs[pairskey] = pairs.get(pairskey, 0) + 1
                skipped = 0
                print msm['msm_id'], msm['prb_id'], src_addr, srcll[0], srcll[1], msm['dst_addr'], dstll[0], dstll[1], int(distance), round(distance / SOL, 1), rtt, first
            except Exception as exc:
                print >>sys.stderr, msm['msm_id'], msm, exc
                skipped += 1

def main():
    if len(sys.argv) > 1:
        for fname in sys.argv[1:]:
            ruler(fname)
    else:
        for fname in os.listdir('msm'):
            if os.path.isfile('msm/'+fname):
                ruler('msm/'+fname)

if __name__ == '__main__':
    main()
