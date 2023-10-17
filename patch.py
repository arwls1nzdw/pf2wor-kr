import copy
import json
import re
import shutil
from glob import glob

import namuwiki
import utils

# apply my translations
data_base = utils.read_json('dist/koKR.json')
for patch_file in glob("patches/**/*-kr.json", recursive=True):
    patch_data = utils.read_json(patch_file)
    for key in patch_data:
        data_base['strings'][key] = patch_data[key]

utils.write_json(data_base, 'dist/koKR.json')

# apply namuwiki translations
data_namu = copy.deepcopy(data_base)
for k, v in namuwiki.scrap_feats().items():
    data_namu['strings'][k] = v
for k, v in namuwiki.scrap_spell().items():
    data_namu['strings'][k] = v
utils.write_json(data_namu, 'dist/koKR-namu.json')


# apply kingmaker translations
data_km = copy.deepcopy(data_base)
data_namu_km = copy.deepcopy(data_namu)
data_en = utils.read_json("dist/enGB.json")
km_en = utils.read_json("kingmaker/enGB.json")
km_kr = utils.read_json("kingmaker/koKR.json")

keys = {}
count = 0
for k, v in data_en['strings'].items():
    if len(v) < 6:
        continue

    if k in km_en and v[:6].lower() == km_en[k][:6].lower():
        if km_kr[k] == data_km['strings'][k]:
            continue
        r = r"<link=\"([a-zA-Z:_\-가-힣]+)\">"
        km_kr[k] = km_kr[k].replace("</link>", "{/g}")
        matches = re.findall(r, km_kr[k])
        for m in matches:
            km_kr[k] = km_kr[k].replace(f"<link=\"{m}\">", f"{{g|{m}}}")
        if "<link=" in km_kr[k]:
            print(k, km_kr[k])
            raise Exception("link not replaced")
        keys[k] = km_kr[k]
        data_km['strings'][k] = km_kr[k]
        data_namu['strings'][k] = km_kr[k]
        count += 1
utils.write_json(data_km, 'dist/koKR-kingmaker.json')
utils.write_json(data_namu_km, 'dist/koKR-namu+km.json')
print("kingmaker patch count:", count)

data_km_namu = copy.deepcopy(data_km)
for k, v in namuwiki.scrap_feats().items():
    data_km_namu['strings'][k] = v
for k, v in namuwiki.scrap_spell().items():
    data_km_namu['strings'][k] = v
utils.write_json(data_km_namu, 'dist/koKR-km+namu.json')

data_list = [
    (data_base, 'dist/koKR_en.json'),
    (data_namu, 'dist/koKR-namu_en.json'),
    (data_km, 'dist/koKR-kingmaker_en.json'),
    (data_namu_km, 'dist/koKR-namu+km_en.json'),
    (data_km_namu, 'dist/koKR-km+namu_en.json'),
]

# 영문 병기 key 목록
enGB = utils.read_json("dist/enGB.json")
영문병기_keys = set()
for f in glob("patches/Act/*.json"):
    data = utils.read_json(f)
    for k in data:
        영문병기_keys.add(k)

for f in glob("patches/Comp/*.json"):
    data = utils.read_json(f)
    for k in data:
        영문병기_keys.add(k)

for d, p in data_list:
    for k in 영문병기_keys:
        if k not in d['strings'] or len(d['strings'][k]) <= 10:
            continue
        d['strings'][k] += f"\n<size=90%>{enGB['strings'][k]}</size>"

    utils.write_json(d, p)

shutil.copyfile('dist/koKR_en.json', r'D:\Games\SteamLibrary\steamapps\common\Pathfinder Second Adventure\Wrath_Data\StreamingAssets\Localization\enGB.json')
shutil.copyfile('dist/koKR-namu.json', r'D:\Games\SteamLibrary\steamapps\common\Pathfinder Second Adventure\Wrath_Data\StreamingAssets\Localization\zhCN.json')

with open('keys.json', 'wt', encoding='utf-8') as f:
    json.dump(keys, f, ensure_ascii=False, indent=4)
