import fnmatch
from glob import glob
import json
from collections import OrderedDict
from functools import partial
from pathlib import Path
import re

from functional import seq

import dataloader


def find_all_stringKeys(data, *prev_paths):
    global en

    for key in data:
        if isinstance(data, dict):
            val = data[key]
        else:
            val = key

        if not isinstance(val, str) and (hasattr(val, '__iter__') or hasattr(val, '__getitem__')):
            yield from find_all_stringKeys(val, *prev_paths, key)
        elif val in en:
            yield val


def find_jbp_files_using_stringKey(string_key):
    global zip

    for p in zip.filelist:
        if p.filename.endswith('/'):
            continue
        data = zip.read_json(p)
        strKeys = list(find_all_stringKeys(data))
        if string_key in strKeys:
            yield p


def filter_by_pattern(*patterns):
    global keySet, zip
    print("filter_by_pattern", patterns)
    ret = set()
    for p in patterns:
        matches = set(fnmatch.filter(nameSet, p))
        ret.update(
            seq(matches)
            .map(lambda p: zip.read_json(p))
            .map(find_all_stringKeys)
            .map(list)
            .flatten()
            .filter(lambda k: k not in keySet)
            .to_set()
        )
        keySet.update(ret)
        nameSet.difference_update(matches)
    return ret


def addSubdirToFilterList(rootDir: str):
    global filters

    if not rootDir.endswith("/"):
        rootDir = f"{rootDir}/"

    arr = []
    for name in nameSet:
        if not name.startswith(rootDir):
            continue

        if name.count('/') == rootDir.count('/') + 1 and name.endswith('/'):
            arr.append((name[:-1], [f'{name}**/*.jbp', f"{name}*.jbp"]))
        elif name.count('/') == rootDir.count("/") and name.endswith('.jbp'):
            arr.append(
                (f"{rootDir}/_Root", [f"{rootDir}/*.jbp", f"{rootDir}/**/*.jbp"]))

    arr.sort(key=lambda t: "z" if t[0][0] == "_" else t[0])
    for name, pattern in arr:
        filters[name] = partial(filter_by_pattern, *pattern)


def 일치하는jbp파일에서JsonPath가포함된StringKey찾기(jbpFilePattern, *jsonPaths):
    global keySet

    def inner(data, *prev_paths):
        for key in data:
            val = data[key]
            if isinstance(val, list):
                continue
            if isinstance(val, dict):
                yield from inner(val, *prev_paths, key)
            elif all(map(lambda p: p in prev_paths, jsonPaths)) and val in en:
                yield val

    matches = set(fnmatch.filter(nameSet, jbpFilePattern))
    ret = seq(matches) \
        .map(lambda p: zip.read_json(p)) \
        .map(inner) \
        .flatten() \
        .to_set()
    keySet.update(ret)
    return ret


zip = dataloader.get_data_bp()

en = dataloader.get_data_en()['strings']
kr = dataloader.get_data_kr()['strings']

nameSet = set(zip.namelist())

filters = {
    "Comp/Arueshalae": partial(filter_by_pattern, '**/*Arueshalae*/**/*.jbp', '**/*Arueshalae*/*.jbp'),
    "Comp/Camelia": partial(filter_by_pattern, '**/*Camelia*/**/*.jbp', '**/*Camelia*/*.jbp', '**/*Camellia*/**/*.jbp', '**/*Camellia*/*.jbp'),
    "Comp/Daeran": partial(filter_by_pattern, '**/*Daeran*/**/*.jbp', '**/*Daeran*/*.jbp'),
    "Comp/Ember": partial(filter_by_pattern, '**/*Ember*/**/*.jbp', '**/*Ember*/*.jbp'),
    "Comp/Finnean": partial(filter_by_pattern, '**/*Finnean*/**/*.jbp', '**/*Finnean*/*.jbp'),
    "Comp/Greybor": partial(filter_by_pattern, '**/*Greybor*/**/*.jbp', '**/*Greybor*/*.jbp', '**/*Grimbor*/**/*.jbp', '**/*Grimbor*/*.jbp'),
    "Comp/Lann": partial(filter_by_pattern, '**/*Lann*/**/*.jbp', '**/*Lann*/*.jbp'),
    "Comp/Nenio": partial(filter_by_pattern, '**/*Nenio*/**/*.jbp', '**/*Nenio*/*.jbp'),
    "Comp/Regill": partial(filter_by_pattern, '**/*Regill*/**/*.jbp', '**/*Regill*/*.jbp'),
    "Comp/Seelah": partial(filter_by_pattern, '**/*Seelah*/**/*.jbp', '**/*Seelah*/*.jbp'),
    "Comp/Sosiel": partial(filter_by_pattern, '**/*Sosiel*/**/*.jbp', '**/*Sosiel*/*.jbp'),
    "Comp/Wenduag": partial(filter_by_pattern, '**/*Wenduag*/**/*.jbp', '**/*Wenduag*/*.jbp'),
    "Comp/Woljif": partial(filter_by_pattern, '**/*Woljif*/**/*.jbp', '**/*Woljif*/*.jbp'),
    "Comp/Ciar": partial(filter_by_pattern, '**/*Ciar*/**/*.jbp', '**/*Ciar*/*.jbp'),
    "Comp/Delamere": partial(filter_by_pattern, '**/*Delamere*/**/*.jbp', '**/*Delamere*/*.jbp'),
    "Comp/Galfrey": partial(filter_by_pattern, '**/*Galfrey*/**/*.jbp', '**/*Galfrey*/*.jbp'),
    "Comp/Kestoglyr": partial(filter_by_pattern, '**/*Kestoglyr*/**/*.jbp', '**/*Kestoglyr*/*.jbp'),
    "Comp/Staunton": partial(filter_by_pattern, '**/*Staunton*/**/*.jbp', '**/*Staunton*/*.jbp'),
    "NPC/Anevia": partial(filter_by_pattern, 'World/**/*Anevia*/**/*.jbp', 'World/**/*Anevia*/*.jbp'),
    "NPC/BartenderFye": partial(filter_by_pattern, 'World/**/*BartenderFye*/**/*.jbp', 'World/**/*BartenderFye*/*.jbp'),
    "NPC/Crinukh": partial(filter_by_pattern, 'World/**/*Crinukh*/**/*.jbp', 'World/**/*Crinukh*/*.jbp'),
    "NPC/Klejm": partial(filter_by_pattern, 'World/**/*Klejm*/**/*.jbp', 'World/**/*Klejm*/*.jbp'),
    "NPC/Nystra": partial(filter_by_pattern, 'World/**/*Nystra*/**/*.jbp', 'World/**/*Nystra*/*.jbp'),
    "NPC/Galfrey": partial(filter_by_pattern, 'World/**/*Galfrey*/**/*.jbp', 'World/**/*Galfrey*/*.jbp'),
    "NPC/GemGolem": partial(filter_by_pattern, 'World/**/*GemGolem*/**/*.jbp', 'World/**/*GemGolem*/*.jbp'),
    "NPC/Horgus": partial(filter_by_pattern, 'World/**/*Horgus*/**/*.jbp', 'World/**/*Horgus*/*.jbp'),
    "NPC/Irabeth": partial(filter_by_pattern, 'World/**/*Irabeth*/**/*.jbp', 'World/**/*Irabeth*/*.jbp'),
    "NPC/Kaylessa": partial(filter_by_pattern, 'World/**/*Kaylessa*/**/*.jbp', 'World/**/*Kaylessa*/*.jbp'),
    "NPC/Lexicon": partial(filter_by_pattern, 'World/**/*Lexicon*/**/*.jbp', 'World/**/*Lexicon*/*.jbp'),
    "NPC/Nura": partial(filter_by_pattern, 'World/**/*Nura*/**/*.jbp', 'World/**/*Nura*/*.jbp'),
    "NPC/ScrollVendor": partial(filter_by_pattern, 'World/**/*ScrollVendor*/**/*.jbp', 'World/**/*ScrollVendor*/*.jbp'),
    "NPC/StoryTeller": partial(filter_by_pattern, 'World/**/*StoryTeller*/**/*.jbp', 'World/**/*StoryTeller*/*.jbp', 'World/**/Collector/*.jbp'),
    "NPC/Vendor": partial(filter_by_pattern, 'World/**/*Vendor*/**/*.jbp', 'World/**/*Vendor*/*.jbp'),
    "NPC/Hilor": partial(filter_by_pattern, 'World/**/*Hilor*/**/*.jbp', 'World/**/*Hilor*/*.jbp'),
    "Mythic/Aeon": partial(filter_by_pattern, 'Mythic/Aeon/**/*.jbp', 'Mythic/Aeon/*.jbp'),
    "Mythic/Angel": partial(filter_by_pattern, 'Mythic/Angel/**/*.jbp', 'Mythic/Angel/*.jbp'),
    "Mythic/Azata": partial(filter_by_pattern, 'Mythic/Azata/**/*.jbp', 'Mythic/Azata/*.jbp'),
    "Mythic/Demon": partial(filter_by_pattern, 'Mythic/Demon/**/*.jbp', 'Mythic/Demon/*.jbp'),
    "Mythic/Devil": partial(filter_by_pattern, 'Mythic/Devil/**/*.jbp', 'Mythic/Devil/*.jbp'),
    "Mythic/Legend": partial(filter_by_pattern, 'Mythic/Legend/**/*.jbp', 'Mythic/Legend/*.jbp'),
    "Mythic/Lich": partial(filter_by_pattern, 'Mythic/Lich/**/*.jbp', 'Mythic/Lich/*.jbp'),
    "Mythic/Dragon": partial(filter_by_pattern, 'Mythic/Dragon/**/*.jbp', 'Mythic/Dragon/*.jbp'),
    "Mythic/Trickster": partial(filter_by_pattern, 'Mythic/Trickster/**/*.jbp', 'Mythic/Trickster/*.jbp', 'Mythic/Feats/TricksterFeats/*.jbp',),
    "Mythic/Swarm": partial(filter_by_pattern, 'Mythic/Swarm/**/*.jbp', 'Mythic/Swarm/*.jbp'),
    "Mythic/Common": partial(filter_by_pattern, 'Mythic/**/*.jbp', 'Mythic/*.jbp'),
    "Act/Chp_0": partial(filter_by_pattern, 'World/**/c0*/**/*.jbp', 'World/Areas/Act_0*/*.jbp'),
    "Act/Chp_1": partial(filter_by_pattern, 'World/**/c1*/**/*.jbp', 'World/Areas/Act_1*/*.jbp'),
    "Act/Chp_2": partial(filter_by_pattern, 'World/**/c2*/**/*.jbp', 'World/Areas/Act_2*/*.jbp'),
    "Act/Chp_3": partial(filter_by_pattern, 'World/**/c3*/**/*.jbp', 'World/Areas/Act_3*/*.jbp'),
    "Act/Chp_4": partial(filter_by_pattern, 'World/**/c4*/**/*.jbp', 'World/Areas/Act_4*/*.jbp'),
    "Act/Chp_5": partial(filter_by_pattern, 'World/**/c5*/**/*.jbp', 'World/Areas/Act_5*/*.jbp'),
    "Act/Chp_6": partial(filter_by_pattern, 'World/**/c6*/**/*.jbp', 'World/Areas/Act_6*/*.jbp'),
    "Act/Epilogue": partial(filter_by_pattern, 'World/**/*Epilogue*/**/*.jbp', 'World/**/*Epilogue*/*.jbp'),
    "Act/DLC_1": partial(filter_by_pattern, 'World/**/*DLC1*/**/*.jbp'),
    "Act/DLC_2": partial(filter_by_pattern, 'World/**/*DLC2*/**/*.jbp'),
    "Act/DLC_3": partial(filter_by_pattern, 'World/**/*DLC3*/**/*.jbp'),
    "Act/DLC_4": partial(filter_by_pattern, 'World/**/*DLC4*/**/*.jbp'),
    "Act/Quest/Mythic/Aeon": partial(filter_by_pattern, 'World/Quests/MythicQuests/Aeon/**/*.jbp'),
    "Act/Quest/Mythic/Angel": partial(filter_by_pattern, 'World/Quests/MythicQuests/Angel/**/*.jbp'),
    "Act/Quest/Mythic/Azata": partial(filter_by_pattern, 'World/Quests/MythicQuests/Azata/**/*.jbp'),
    "Act/Quest/Mythic/Demon": partial(filter_by_pattern, 'World/Quests/MythicQuests/Demon/**/*.jbp'),
    "Act/Quest/Mythic/Devil": partial(filter_by_pattern, 'World/Quests/MythicQuests/Devil/**/*.jbp'),
    "Act/Quest/Mythic/Dragon": partial(filter_by_pattern, 'World/Quests/MythicQuests/Dragon/**/*.jbp'),
    "Act/Quest/Mythic/Legend": partial(filter_by_pattern, 'World/Quests/MythicQuests/Legend/**/*.jbp'),
    "Act/Quest/Mythic/Lich": partial(filter_by_pattern, 'World/Quests/MythicQuests/Lich/**/*.jbp'),
    "Act/Quest/Mythic/Swarm": partial(filter_by_pattern, 'World/Quests/MythicQuests/Locust/**/*.jbp'),
    "Act/Quest/Mythic/Trickster": partial(filter_by_pattern, 'World/Quests/MythicQuests/Trickster/**/*.jbp'),
    "Crusade/Relics/Act_2": partial(filter_by_pattern, 'World/Crusade/Events/Relics/Ch2/*.jbp'),
    "Crusade/Relics/Act_3": partial(filter_by_pattern, 'World/Crusade/Events/Relics/Ch3/*.jbp'),
    "Crusade/Relics/Act_4": partial(filter_by_pattern, 'World/Crusade/Events/Relics/Ch4/*.jbp'),
    "Crusade/Relics/Act_5": partial(filter_by_pattern, 'World/Crusade/Events/Relics/Ch5/*.jbp'),
    "Crusade/RankUp/Diplomacy": partial(filter_by_pattern, "World/Crusade/RankUps/Diplomacy/**/*.jbp"),
    "Crusade/RankUp/Leadership": partial(filter_by_pattern, "World/Crusade/RankUps/Leadership/**/*.jbp"),
    "Crusade/RankUp/Logistic": partial(filter_by_pattern, "World/Crusade/RankUps/Logistics/**/*.jbp"),
    "Crusade/RankUp/Military": partial(filter_by_pattern, "World/Crusade/RankUps/Military/**/*.jbp"),
    "Crusade/RankUp/Mythic/Aeon": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Aeon/**/*.jbp"),
    "Crusade/RankUp/Mythic/Angel": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Angel/**/*.jbp"),
    "Crusade/RankUp/Mythic/Azata": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Azata/**/*.jbp"),
    "Crusade/RankUp/Mythic/Demon": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Demon/**/*.jbp"),
    "Crusade/RankUp/Mythic/Dragon": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Dragon/**/*.jbp"),
    "Crusade/RankUp/Mythic/Legend": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Legend/**/*.jbp"),
    "Crusade/RankUp/Mythic/Lich": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Lich/**/*.jbp"),
    "Crusade/RankUp/Mythic/Swarm": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Locust/**/*.jbp"),
    "Crusade/RankUp/Mythic/Trickster": partial(filter_by_pattern, "World/Crusade/RankUps/MythicRankUps/Trickster/**/*.jbp"),
    "Crusade/Items": partial(filter_by_pattern, 'World/Crusade/CrusadeItems/**/*.jbp'),
    "Crusade/Army": partial(filter_by_pattern, 'World/Crusade/CrusadeArmy/**/*.jbp'),
    "Crusade/Quests": partial(filter_by_pattern, 'World/Quests/Crusade/**/*.jbp'),
}

addSubdirToFilterList("Spells")
addSubdirToFilterList("Classes")
addSubdirToFilterList("Feats")
addSubdirToFilterList("Equipment")
addSubdirToFilterList("Items")
addSubdirToFilterList("Armies")
addSubdirToFilterList("Units")
addSubdirToFilterList("Weapons/Items")
addSubdirToFilterList("Weapons")
addSubdirToFilterList("World")

rootdirs = seq(zip.filelist) \
    .filter(lambda f: f.filename.endswith('/') and f.filename.count('/') == 1) \
    .map(lambda f: f.filename[:-1]) \
    .to_list()
filters = {
    **filters,
    **{d: partial(filter_by_pattern, f'{d}/**/*.jbp', f'{d}/*.jbp') for d in rootdirs if d not in filters}
}

keySet = set()

data = {}
data['Shared/Location'] = [
    *일치하는jbp파일에서JsonPath가포함된StringKey찾기("**/Location*.jbp", "Name"),
    *일치하는jbp파일에서JsonPath가포함된StringKey찾기("**/*.jbp", "AreaName")
]
data['Shared/Duration'] = 일치하는jbp파일에서JsonPath가포함된StringKey찾기(
    "**/*.jbp", "LocalizedDuration")
data['Shared/SavingThrow'] = 일치하는jbp파일에서JsonPath가포함된StringKey찾기(
    "**/*.jbp", "LocalizedSavingThrow")
for key in filters:
    data[key] = filters[key]()
data['missing'] = [k for k in en if k not in keySet]


def dump_with_sort(fname, data):
    d2 = dict(sorted(data.items(), key=lambda t: (en[t[0]], t[0])))
    Path(fname).write_text(json.dumps(
        d2, ensure_ascii=False, indent=4), encoding='utf-8')


def isDummy(text: str):
    if len(text) == 0:
        return True
    if text.lower().strip().startswith('[draft]'):
        return True
    if text.lower().strip().startswith('(draft)'):
        return True
    if '[Драфт]' in text:
        return True
    return False


file_list = set()
for name in data:
    parent = ''
    stem = name
    if '/' in name:
        parent = '/'.join(name.split('/')[:-1])
        if not parent.endswith('/'):
            parent = f'{parent}/'

        Path(f'patches/{parent}').mkdir(parents=True, exist_ok=True)
        parent = f'{parent}/'
        stem = name.split('/')[-1]

    out_en = {}
    out_kr = {}
    for key in data[name]:
        v_en = en[key]
        v_kr = kr[key] if key in kr else v_en
        if isDummy(v_en):
            continue
        out_en[key] = v_en
        out_kr[key] = v_kr

    if len(out_en) == 0:
        print('skip empty', name)
        continue
    dump_with_sort(f'patches/{parent}{stem}-en.json', out_en)
    dump_with_sort(f'patches/{parent}{stem}-kr.json', out_kr)
    file_list.add(f'patches/{parent}{stem}-en.json')
    file_list.add(f'patches/{parent}{stem}-kr.json')

for f in glob("patches/**/*.json"):
    f = f.replace('\\', '/')
    if f not in file_list:
        print(f)

print("=======summary=======")
for key in sorted(data.keys(), key=lambda d: len(data[d])):
    if len(data[key]) == 0:
        continue
    print(
        f"{key:20s}: {len(data[key]):>6,}({len(data[key]) / len(en) * 100:.2f}%)")
