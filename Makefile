.PHONY: all
all:
	:

20170130.json.bz2:
	wget ftp://ftp.ripe.net/ripe/atlas/probes/archive/2017/01/20170130.json.bz2

20170130.json: 20170130.json.bz2
	bzcat <$^ >$@

meta-20170130.txt.bz2:
	wget ftp://ftp.ripe.net/ripe/atlas/measurements/meta-20170130.txt.bz2

# full dump is 16Gb, bz2 is 892M but bzcat takes 10 minutes, lz4 is 2.3Gb but takes 10 seconds to lz4cat
meta-20170130.txt.lz4: meta-20170130.txt.bz2
	bzcat meta-20170130.txt.bz2 | lz4 -5c >meta-20170130.txt.lz4

country-resource-list_ru_20170130.json:
	wget -O $@ 'https://stat.ripe.net/data/country-resource-list/data.json?resource=ru&time=2017-01-30&v4_format=prefix'

asn_20170130.pickle: country-resource-list_ru_20170130.json
	./mkasn.py <$^ >$@

24bitarray_20170130.pickle: country-resource-list_ru_20170130.json
	./mk24bit.py <$^ >$@

geo24_20170130.pickle: 20170130.json
	./mkgeo24.py <$^ >$@

prbids_20170130.pickle: 20170130.json
	./mkruprb.py <$^ >$@

geo24_dst_meta-20170130.txt.lz4: meta-20170130.txt.lz4
	python -c 'from datadict import *; map(sys.stdout.write, ("\x22dst_addr\x22:\x22" + str(IPAddress(i << 8, version=4)).rsplit(".", 1)[0] + ".\n" for i in geo24.iterkeys()))' >geo24_dst_meta-20170130.prefilter
	lz4cat <$^ | grep --fixed-strings --file geo24_dst_meta-20170130.prefilter | lz4 -5 >$@
