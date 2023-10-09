import json
from glob import glob

import utils

owlcats_en = {}
owlcats_kr = {}
for p in glob('patches/*-en.json'):
    d = utils.read_json(p)
    for k, v in d.items():
        if 'Owlcat' in v:
            owlcats_en[k] = v


for en in glob('patches/*-en.json'):
    d = utils.read_json(en)
    for o in owlcats_en:
        if o in d:
            del d[o]
    utils.write_json(d, en)

for kr in glob('patches/*-kr.json'):
    d = utils.read_json(kr)
    for o in owlcats_en:
        if o in d:
            owlcats_kr[o] = d[o]
            del d[o]
    utils.write_json(d, kr)

utils.write_json(owlcats_en, 'patches/Owlcats-en.json')
utils.write_json(owlcats_kr, 'patches/Owlcats-kr.json')
