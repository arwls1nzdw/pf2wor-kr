import fnmatch
import json
import os
import zipfile
from collections import OrderedDict
from functools import partial
from pathlib import Path

from functional import seq

zip = zipfile.ZipFile("D:/Games/SteamLibrary/steamapps/common/Pathfinder Second Adventure/blueprints.zip")

en = json.loads(Path('dist/enGB.json').read_text(encoding='utf-8'))['strings']
kr = json.loads(Path('dist/koKR.json').read_text(encoding='utf-8'))['strings']

path_set = set()


def print_path_of_val(dic, val, *prev_paths):
    for key in dic:
        v = dic[key]
        if isinstance(v, dict):
            print_path_of_val(v, val, *prev_paths, key)
        elif v == val:
            print(type(v))
            p = '.'.join(prev_paths + (key,))
            if p not in path_set:
                path_set.add(p)
                print(p)


def find_string_keys(data, *prev_paths):
    global en
    for key in data:
        if isinstance(data, dict):
            val = data[key]
        else:
            val = key

        if not isinstance(val, str) and (hasattr(val, '__iter__') or hasattr(val, '__getitem__')):
            yield from find_string_keys(val, *prev_paths, key)
        elif val in en:
            # print_path_of_val(data, val, *prev_paths, key)
            yield val


def find_string_key_file(string_key):
    global zip
    for p in zip.filelist:
        if p.filename.endswith('/'):
            continue
        data = json.loads(zip.read(p).decode('utf-8'))
        strKeys = list(find_string_keys(data))
        if string_key in strKeys:
            yield p


keySet = set()

namelist = set(zip.namelist())


def filter_by_pattern(*patterns):
    global keySet, zip
    print("filter_by_pattern", patterns)
    ret = set()
    for p in patterns:
        matches = set(fnmatch.filter(namelist, p))
        ret.update(
            seq(matches)
            .map(lambda p: zip.read(p).decode('utf-8'))
            .map(lambda d: json.loads(d))
            .map(find_string_keys)
            .map(list)
            .flatten()
            .filter(lambda k: k not in keySet)
            .to_set()
        )
        keySet.update(ret)
        namelist.difference_update(matches)
    return ret


def find_file_using_key(key):
    global zip

    def inner(data):
        for k in data:
            val = data[k]
            if isinstance(val, list):
                continue
            if isinstance(val, dict):
                return inner(val)
            elif val == key:
                return True
        return False

    for p in zip.filelist:
        if p.filename.endswith('/'):
            continue
        data = json.loads(zip.read(p).decode('utf-8'))
        if inner(data):
            return p
    return None


def addSubdirToFilterList(rootDir):
    global filters

    arr = []
    for name in namelist:
        if not name.startswith(f"{rootDir}/"):
            continue
        if name.count('/') == 2 and name.endswith('/'):
            arr.append((name, [f'{name}**/*.jbp', f"{name}*.jbp"]))
            filters[name] = partial(filter_by_pattern, )
        elif name.count('/') == 1 and name.endswith('.jbp'):
            arr.append((f"{rootDir}/_Root", [f"{rootDir}/*.jbp"]))

    arr.sort(key=lambda t: "z" if t[0][0] == "_" else t[0])
    for name, pattern in arr:
        filters[name] = partial(filter_by_pattern, *pattern)


# 가장 나중에 필터링

rootdirs = seq(zip.filelist) \
    .filter(lambda f: f.filename.endswith('/') and f.filename.count('/') == 1) \
    .map(lambda f: f.filename[:-1]) \
    .to_list()

# list(find_string_key_file("bde17a0e-91cf-4367-88a0-fbe62311eb13"))

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
    "Mythic/Aeon": partial(filter_by_pattern, 'Mythic/*Aeon*/**/*.jbp', 'World/Areas/Mythics/Aeon*/**/*.jbp', 'World/Quests/MythicQuests/Aeon/**/*.jbp'),
    "Mythic/Angel": partial(filter_by_pattern, 'Mythic/*Angel*/**/*.jbp', 'World/Quests/MythicQuests/Angel/**/*.jbp'),
    "Mythic/Azata": partial(filter_by_pattern, 'Mythic/*Azata*/**/*.jbp', 'World/Quests/MythicQuests/Azata/**/*.jbp'),
    "Mythic/Demon": partial(filter_by_pattern, 'Mythic/*Demon*/**/*.jbp', 'World/Quests/MythicQuests/Demon/**/*.jbp'),
    "Mythic/Devil": partial(filter_by_pattern, 'Mythic/*Devil*/**/*.jbp', 'World/Quests/MythicQuests/Devil/**/*.jbp'),
    "Mythic/Legend": partial(filter_by_pattern, 'Mythic/*Legend*/**/*.jbp', 'World/Areas/Mythics/Legend*/**/*.jbp', 'World/Quests/MythicQuests/Legend/**/*.jbp'),
    "Mythic/Lich": partial(filter_by_pattern, 'Mythic/*Lich*/**/*.jbp', 'World/Quests/MythicQuests/Lich/**/*.jbp'),
    "Mythic/Dragon": partial(filter_by_pattern, 'Mythic/*Dragon*/**/*.jbp', 'World/Quests/MythicQuests/Dragon/**/*.jbp'),
    "Mythic/Trickster": partial(filter_by_pattern, 'Mythic/*Trickster*/**/*.jbp', 'Mythic/Feats/TricksterFeats/*.jbp', 'World/Areas/Mythics/Trickster*/**/*.jbp', 'World/Quests/MythicQuests/Trickster/**/*.jbp'),
    "Mythic/Swarm": partial(filter_by_pattern, 'Mythic/*Swarm*/**/*.jbp', 'World/Quests/MythicQuests/Locust/**/*.jbp'),
    "Mythic/Common": partial(filter_by_pattern, 'Mythic/**/*.jbp'),
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
    "Crusade": partial(filter_by_pattern, '**/*Crusade*/**/*.jbp'),
}

addSubdirToFilterList("Classes")
addSubdirToFilterList("Spells")
addSubdirToFilterList("Feats")
addSubdirToFilterList("Equipment")
addSubdirToFilterList("Items")
addSubdirToFilterList("Armies")
addSubdirToFilterList("Units")

filters = {
    **filters,
    **{d: partial(filter_by_pattern, f'{d}/**/*.jbp') for d in rootdirs if d not in filters}
}

for k in filters.keys():
    print(k)

data = {}
keySet = set()
for key in filters:
    data[key] = filters[key]()
data['missing'] = [k for k in en if k not in keySet]


def dump_with_sort(fname, data):
    data = OrderedDict(sorted(data.items(), key=lambda t: (en[t[0]], t[1])))
    Path(fname).write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')


def isDummy(text: str):
    if len(text) == 0:
        return True
    if text.lower().strip().startswith('[draft]'):
        return True
    if text.lower().strip().startswith('(draft)'):
        return True
    return False


for name in data:
    path = ''
    stem = name
    if '/' in name:
        parent = name.split('/')[0]
        Path(f'patches/{parent}').mkdir(parents=True, exist_ok=True)
        path = f'{parent}/'
        stem = name.split('/')[1]
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
    dump_with_sort(f'patches/{path}{stem}-en.json', out_en)
    dump_with_sort(f'patches/{path}{stem}-kr.json', out_kr)

print("=======summary=======")
for key in sorted(data.keys(), key=lambda d: len(data[d])):
    if len(data[key]) == 0:
        continue
    print(f"{key:20s}: {len(data[key]):>6,}({len(data[key]) / len(en) * 100:.2f}%)")
