import json
from glob import glob

import utils
from blueprint import isDummy

data_prev = json.load(open('dist/enGB.json.prev', 'rt',
                      encoding='utf-8'))['strings']
data_curr = json.load(
    open('dist/enGB.json', 'rt', encoding='utf-8'))['strings']


data_kr = json.load(open('dist/koKR.json', 'rt',
                         encoding='utf-8'))['strings']
diffs = {}
for key in data_curr:
    if isDummy(data_curr[key]):
        continue

    a = data_prev[key] if key in data_prev else None
    b = data_curr[key]
    c = data_kr[key] if key in data_kr else None
    if utils.remove_tags(a) != utils.remove_tags(b):
        diffs[key] = [a, b, c]

for f in glob("patches/**/*-en.json", recursive=True):
    data = json.load(open(f, 'rt', encoding='utf-8'))
    for key in data:
        if key not in diffs:
            continue
        data[key] = diffs[key][1]

    utils.write_json(data, f)

json.dump(diffs, open('diff.json', 'wt', encoding='utf-8'),
          indent=4, ensure_ascii=False)

print(len(diffs))
