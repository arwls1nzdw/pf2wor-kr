import copy
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

count = 0
for k, v in data_en['strings'].items():
    if len(v) < 3:
        continue

    if k in km_en and v[:3].lower() == km_en[k][:3].lower():
        if km_kr[k] == data_kingmaker['strings'][k]:
            continue
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
