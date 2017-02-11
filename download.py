#!/usr/bin/env python2.7

import ujson
import sys
from subprocess import Popen, PIPE
import requests
import tempfile
import multiprocessing.dummy as mp

from datadict import *

def download(url, dest):
    assert not os.path.exists(dest)
    print 'Downloading', dest
    with tempfile.NamedTemporaryFile(prefix='tmpmsm', dir='.') as rawfd:
        proc = Popen(['lz4', '-5'], stdin=PIPE, stdout=rawfd)
        req = requests.get(url, stream=True, timeout=15.)
        for blob in req.iter_content(chunk_size=16*1024, decode_unicode=False):
            proc.stdin.write(blob)
        proc.stdin.flush()
        proc.stdin.close()
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError('lz4 failed', proc.returncode)
        os.link(rawfd.name, dest)

def main():
    fetchlist = []
    for doc in sys.stdin:
        doc = ujson.loads(doc) # NB: trailing whitespace is not a big deal for `ujson`
        if doc['type']['name'] in ('ping', 'traceroute'):
            src = map(str, (p['id'] for p in doc['probes'] if p['id'] in geoprb))
            url = 'https://atlas.ripe.net/api/v2/measurements/{}/results/?start={}&probe_ids={}&format=txt'.format(
                        doc['msm_id'], 1483228800, ','.join(src))
            dest = 'msm/{}.json.lz4'.format(doc['msm_id'])
            if not os.path.exists(dest):
                fetchlist.append( (url, dest) )
            else:
                print 'Skipping', dest
    pool = mp.Pool(processes=8)
    pool.map(lambda x: download(*x), fetchlist, chunksize=1)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
