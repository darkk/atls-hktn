#!/usr/bin/env python2.7

import itertools
import sys
from operator import itemgetter

def stream():
    for line in sys.stdin:
        # 3315654 10001 212.238.160.244 52.3875 4.8875 170.210.5.200 -34.6025 -58.3795 11446 110.7 231.365695 nan
        msm_id, prb_id, src, srclat, srclon, dst, dstlat, dstlon, distance, light, rtt, first = line.rstrip().split()
        msm_id, prb_id, distance = map(int, (msm_id, prb_id, distance))
        srclat, srclon, dstlat, dstlon, light, rtt, first = map(float, (srclat, srclon, dstlat, dstlon, light, rtt, first))
        yield msm_id, prb_id, src, srclat, srclon, dst, dstlat, dstlon, distance, light, rtt, first

def main():
    for prb_id, it in itertools.groupby(stream(), itemgetter(1)):
        prbinfo = list(it)
        for t in prbinfo:
            msm_id, prb_id, src, srclat, srclon, dst, dstlat, dstlon, distance, light, rtt, first = t
            if distance > 15 and rtt < light / 2.: # factor of 2 error!
                print ' '.join(map(str, t))

if __name__ == '__main__':
    main()
