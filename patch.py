import copy
import json
import re
import shutil
from glob import glob

import namuwiki
import utils

# apply my translations
data = utils.read_json('dist/koKR.json')
for patch_file in glob("patches/**/*-kr.json", recursive=True):
    patch_data = utils.read_json(patch_file)
    for key in patch_data:
        data['strings'][key] = patch_data[key]

utils.write_json(data, 'dist/koKR.json')

# apply namuwiki translations
data_namu = copy.deepcopy(data)
for k, v in namuwiki.scrap_feats().items():
    data_namu['strings'][k] = v
for k, v in namuwiki.scrap_spell().items():
    data_namu['strings'][k] = v
utils.write_json(data_namu, 'dist/koKR-namu.json')


# apply kingmaker translations
data_kingmaker = copy.deepcopy(data)
data_en = utils.read_json("dist/enGB.json")
km_en = utils.read_json("kingmaker/enGB.json")
km_kr = utils.read_json("kingmaker/koKR.json")

keys = {}
count = 0
for k, v in data_en['strings'].items():
    if len(v) < 6:
        continue

    if k in km_en and v[:6].lower() == km_en[k][:6].lower():
        if km_kr[k] == data_kingmaker['strings'][k]:
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
        data_kingmaker['strings'][k] = km_kr[k]
        data_namu['strings'][k] = km_kr[k]
        count += 1
utils.write_json(data_kingmaker, 'dist/koKR-kingmaker.json')
utils.write_json(data_kingmaker, 'dist/koKR-namu+km.json')
print("kingmaker patch count:", count)

for k, v in namuwiki.scrap_feats().items():
    data_kingmaker['strings'][k] = v
for k, v in namuwiki.scrap_spell().items():
    data_kingmaker['strings'][k] = v
utils.write_json(data_kingmaker, 'dist/koKR-km+namu.json')

shutil.copyfile('dist/koKR.json', r'D:\Games\SteamLibrary\steamapps\common\Pathfinder Second Adventure\Wrath_Data\StreamingAssets\Localization\enGB.json')
shutil.copyfile('dist/koKR-namu.json', r'D:\Games\SteamLibrary\steamapps\common\Pathfinder Second Adventure\Wrath_Data\StreamingAssets\Localization\zhCN.json')

with open('keys.json', 'wt', encoding='utf-8') as f:
    json.dump(keys, f, ensure_ascii=False, indent=4)
