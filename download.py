#!/usr/bin/env python2.7

import ujson
import random
import sys
from subprocess import Popen, PIPE
import requests
import tempfile
import multiprocessing.dummy as mp

from datadict import *

def download(url, dest):
    assert not os.path.exists(dest)
    proc = None

    try:
        print 'Downloading', dest
        with tempfile.NamedTemporaryFile(prefix='tmpmsm', dir='.') as rawfd:
            proc = Popen(['lz4', '-5'], stdin=PIPE, stdout=rawfd)
            req = requests.get(url, stream=True, timeout=15.)
            for blob in req.iter_content(chunk_size=16*1024, decode_unicode=False):
                proc.stdin.write(blob)
                stat = os.statvfs('.')
                stat = stat.f_bavail * 1. / stat.f_blocks
                if stat < 0.01:
                    raise RuntimeError('Less than 2% free, see `df -h`', stat)
            proc.stdin.flush()
            proc.stdin.close()
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError('lz4 failed', proc.returncode)
            os.link(rawfd.name, dest)
    except Exception as exc:
        print 'Failed', dest, '->', str(exc)
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                proc.wait()
            except Exception:
                pass

def main():
    fetchlist = {}
    for doc in sys.stdin:
        doc = ujson.loads(doc) # NB: trailing whitespace is not a big deal for `ujson`
        if doc['type']['name'] in ('ping', 'traceroute'):
            src = map(str, (p['id'] for p in doc['probes'] if p['id'] in geoprb))
            dest = 'msm/{}.json.lz4'.format(doc['msm_id'])
            if not os.path.exists(dest):
                stop_time = doc['stop_time']
                if stop_time is None:
                    stop_time = 1485820800 # Jan 31 2017
                stop_time = min(stop_time, 1485820800)

                start_time = doc['start_time']
                while start_time < stop_time:
                    thisstop = min(stop_time, start_time + 24*3600)
                    dest = 'msm/{}-{}-{}.json.lz4'.format(doc['msm_id'], start_time, thisstop)
                    url = 'https://atlas.ripe.net/api/v2/measurements/{}/results/?start={}&stop={}&probe_ids={}&format=txt'.format(
                                doc['msm_id'], start_time, thisstop, ','.join(src))
                    start_time = thisstop
                    if not os.path.exists(dest):
                        fetchlist.setdefault(doc['msm_id'], []).append( (url, dest) )
                    else:
                        print 'Skipping', dest
            else:
                print 'Skipping', dest
    for k in fetchlist.keys():
        random.shuffle(fetchlist[k])
    flattened = []
    while len(fetchlist):
        msm_id = random.choice(fetchlist.keys())
        pair = random.choice(fetchlist[msm_id])
        flattened.append(pair)
        fetchlist[msm_id].remove(pair)
        if not len(fetchlist[msm_id]):
            del fetchlist[msm_id]
            if len(fetchlist) % 100 == 0:
                print 'Remaining unscheduled measurements...', len(fetchlist)
    pool = mp.Pool(processes=8)
    pool.map(lambda x: download(*x), flattened, chunksize=1)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
