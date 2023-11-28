import fnmatch
import json
import os
import re
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from functional import seq

import dataloader

zip = dataloader.get_data_bp()
en = dataloader.get_data_en()['strings']
kr = dataloader.get_data_kr()['strings']


def find_all_stringKeys(data, *prev_paths):
    iter = data
    if isinstance(data, list):
        iter = [i for i in range(len(data))]

    for key in iter:
        val = data[key]

        if not isinstance(val, str) and (hasattr(val, '__iter__') or hasattr(val, '__getitem__')):
            yield from find_all_stringKeys(val, *prev_paths, key)
        if isinstance(val, str) and val in en:
            yield val
        if isinstance(key, str) and key in en:
            yield key


def filter_by_pattern(patterns):
    ret = set()
    for p in patterns:
        ret.update(
            seq(fnmatch.filter(zip.namelist(), p))
            .map(lambda p: zip.read_json(p))
            .map(find_all_stringKeys)
            .map(list)
            .flatten()
            .to_set()
        )
    return ret


def addSubdirToFilterList(filters: dict, rootDir: str):
    if not rootDir.endswith('/'):
        rootDir = f'{rootDir}/'

    arr = []
    for name in zip.namelist():
        if not name.startswith(rootDir):
            continue

        if name.count('/') == rootDir.count('/') + 1 and name.endswith('/'):
            arr.append((name[:-1], [f'{name}**/*.jbp', f'{name}*.jbp']))
        elif name.count('/') == rootDir.count('/') and name.endswith('.jbp'):
            arr.append(
                (f'{rootDir}/_Root', [f'{rootDir}/*.jbp', f'{rootDir}/**/*.jbp']))

    arr.sort(key=lambda t: 'z' if t[0][0] == '_' else t[0])
    for name, pattern in arr:
        if name not in filters:
            filters[name] = []
        filters[name].extend(pattern)


def searchStringKey(jbpFilePattern, *jsonPaths):
    def inner(data, *prev_paths):
        iter = data
        if isinstance(data, list):
            iter = [i for i in range(len(data))]

        for key in iter:
            val = data[key]
            if isinstance(val, list):
                yield from inner(val, *prev_paths, f'[{key}]')
            if isinstance(val, dict):
                yield from inner(val, *prev_paths, key)
            elif all(map(lambda p: p in prev_paths, jsonPaths)) and val in en:
                yield val

    matches = set(fnmatch.filter(zip.namelist(), jbpFilePattern))
    ret = seq(matches) \
        .map(lambda p: zip.read_json(p)) \
        .map(inner) \
        .flatten() \
        .to_set()
    return ret


def isDummy(text: str):
    if len(text) == 0:
        return True
    if text.lower().strip().startswith('[draft]'):
        return True
    if text.lower().strip().startswith('(draft)'):
        return True
    rgx_en = r'[a-zA-Z]'
    rgx_ru = r'[а-яА-ЯёЁ]'
    if re.search(rgx_ru, text) and not re.search(rgx_en, text):
        return True
    return False


def writeOrUnlink(data, path):
    if len(data) == 0:
        if path.exists():
            path.unlink()
        return

    del_keys = []
    for k in data.keys():
        if isDummy(en[k]):
            del_keys.append(k)
    for k in del_keys:
        del data[k]

    data = dict(sorted(data.items(), key=lambda x: (en[x[0]], x[0])))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wt', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    pool = ProcessPoolExecutor(max_workers=os.cpu_count())

    filters = OrderedDict()

    filters = {
        'Comp/Arueshalae': ['**/*Arueshalae*/**/*.jbp', '**/*Arueshalae*/*.jbp'],
        'Comp/Camelia': ['**/*Camelia*/**/*.jbp', '**/*Camelia*/*.jbp', '**/*Camellia*/**/*.jbp', '**/*Camellia*/*.jbp'],
        'Comp/Daeran': ['**/*Daeran*/**/*.jbp', '**/*Daeran*/*.jbp'],
        'Comp/Ember': ['**/*Ember*/**/*.jbp', '**/*Ember*/*.jbp'],
        'Comp/Finnean': ['**/*Finnean*/**/*.jbp', '**/*Finnean*/*.jbp'],
        'Comp/Greybor': ['**/*Greybor*/**/*.jbp', '**/*Greybor*/*.jbp', '**/*Grimbor*/**/*.jbp', '**/*Grimbor*/*.jbp'],
        'Comp/Lann': ['**/*Lann*/**/*.jbp', '**/*Lann*/*.jbp'],
        'Comp/Nenio': ['**/*Nenio*/**/*.jbp', '**/*Nenio*/*.jbp'],
        'Comp/Regill': ['**/*Regill*/**/*.jbp', '**/*Regill*/*.jbp'],
        'Comp/Seelah': ['**/*Seelah*/**/*.jbp', '**/*Seelah*/*.jbp'],
        'Comp/Sosiel': ['**/*Sosiel*/**/*.jbp', '**/*Sosiel*/*.jbp'],
        'Comp/Wenduag': ['**/*Wenduag*/**/*.jbp', '**/*Wenduag*/*.jbp'],
        'Comp/Woljif': ['**/*Woljif*/**/*.jbp', '**/*Woljif*/*.jbp'],
        'Comp/Ciar': ['**/*Ciar*/**/*.jbp', '**/*Ciar*/*.jbp'],
        'Comp/Delamere': ['**/*Delamere*/**/*.jbp', '**/*Delamere*/*.jbp'],
        'Comp/Galfrey': ['**/*Galfrey*/**/*.jbp', '**/*Galfrey*/*.jbp'],
        'Comp/Kestoglyr': ['**/*Kestoglyr*/**/*.jbp', '**/*Kestoglyr*/*.jbp'],
        'Comp/Staunton': ['**/*Staunton*/**/*.jbp', '**/*Staunton*/*.jbp'],
        'NPC/Anevia': ['World/**/*Anevia*/**/*.jbp', 'World/**/*Anevia*/*.jbp'],
        'NPC/BartenderFye': ['World/**/*BartenderFye*/**/*.jbp', 'World/**/*BartenderFye*/*.jbp'],
        'NPC/Crinukh': ['World/**/*Crinukh*/**/*.jbp', 'World/**/*Crinukh*/*.jbp'],
        'NPC/Klejm': ['World/**/*Klejm*/**/*.jbp', 'World/**/*Klejm*/*.jbp'],
        'NPC/Nystra': ['World/**/*Nystra*/**/*.jbp', 'World/**/*Nystra*/*.jbp'],
        'NPC/Galfrey': ['World/**/*Galfrey*/**/*.jbp', 'World/**/*Galfrey*/*.jbp'],
        'NPC/GemGolem': ['World/**/*GemGolem*/**/*.jbp', 'World/**/*GemGolem*/*.jbp'],
        'NPC/Horgus': ['World/**/*Horgus*/**/*.jbp', 'World/**/*Horgus*/*.jbp'],
        'NPC/Irabeth': ['World/**/*Irabeth*/**/*.jbp', 'World/**/*Irabeth*/*.jbp'],
        'NPC/Kaylessa': ['World/**/*Kaylessa*/**/*.jbp', 'World/**/*Kaylessa*/*.jbp'],
        'NPC/Lexicon': ['World/**/*Lexicon*/**/*.jbp', 'World/**/*Lexicon*/*.jbp'],
        'NPC/Nura': ['World/**/*Nura*/**/*.jbp', 'World/**/*Nura*/*.jbp'],
        'NPC/ScrollVendor': ['World/**/*ScrollVendor*/**/*.jbp', 'World/**/*ScrollVendor*/*.jbp'],
        'NPC/StoryTeller': ['World/**/*StoryTeller*/**/*.jbp', 'World/**/*StoryTeller*/*.jbp', 'World/**/Collector/*.jbp'],
        'NPC/Vendor': ['World/**/*Vendor*/**/*.jbp', 'World/**/*Vendor*/*.jbp'],
        'NPC/Hilor': ['World/**/*Hilor*/**/*.jbp', 'World/**/*Hilor*/*.jbp'],
        'Mythic/Aeon': ['Mythic/Aeon/**/*.jbp', 'Mythic/Aeon/*.jbp'],
        'Mythic/Angel': ['Mythic/Angel/**/*.jbp', 'Mythic/Angel/*.jbp'],
        'Mythic/Azata': ['Mythic/Azata/**/*.jbp', 'Mythic/Azata/*.jbp'],
        'Mythic/Demon': ['Mythic/Demon/**/*.jbp', 'Mythic/Demon/*.jbp'],
        'Mythic/Devil': ['Mythic/Devil/**/*.jbp', 'Mythic/Devil/*.jbp'],
        'Mythic/Legend': ['Mythic/Legend/**/*.jbp', 'Mythic/Legend/*.jbp'],
        'Mythic/Lich': ['Mythic/Lich/**/*.jbp', 'Mythic/Lich/*.jbp'],
        'Mythic/Dragon': ['Mythic/Dragon/**/*.jbp', 'Mythic/Dragon/*.jbp'],
        'Mythic/Trickster': ['Mythic/Trickster/**/*.jbp', 'Mythic/Trickster/*.jbp', 'Mythic/Feats/TricksterFeats/*.jbp'],
        'Mythic/Swarm': ['Mythic/Swarm/**/*.jbp', 'Mythic/Swarm/*.jbp'],
        'Mythic/Common': ['Mythic/**/*.jbp', 'Mythic/*.jbp'],
        'Act/Chp_0': ['World/**/c0*/**/*.jbp', 'World/Areas/Act_0*/*.jbp'],
        'Act/Chp_1': ['World/**/c1*/**/*.jbp', 'World/Areas/Act_1*/*.jbp'],
        'Act/Chp_2': ['World/**/c2*/**/*.jbp', 'World/Areas/Act_2*/*.jbp'],
        'Act/Chp_3': ['World/**/c3*/**/*.jbp', 'World/Areas/Act_3*/*.jbp'],
        'Act/Chp_4': ['World/**/c4*/**/*.jbp', 'World/Areas/Act_4*/*.jbp'],
        'Act/Chp_5': ['World/**/c5*/**/*.jbp', 'World/Areas/Act_5*/*.jbp'],
        'Act/Chp_6': ['World/**/c6*/**/*.jbp', 'World/Areas/Act_6*/*.jbp'],
        'Act/Epilogue': ['World/**/*Epilogue*/**/*.jbp', 'World/**/*Epilogue*/*.jbp'],
        'Act/DLC_1': ['World/**/*DLC1*/**/*.jbp'],
        'Act/DLC_2': ['World/**/*DLC2*/**/*.jbp'],
        'Act/DLC_3': ['World/**/*DLC3*/**/*.jbp'],
        'Act/DLC_4': ['World/**/*DLC4*/**/*.jbp'],
        'Act/DLC_5': ['World/**/*DLC5*/**/*.jbp'],
        'Act/DLC_6': ['World/**/*DLC6*/**/*.jbp'],
        'Act/Quest/Mythic/Aeon': ['World/Quests/MythicQuests/Aeon/**/*.jbp'],
        'Act/Quest/Mythic/Angel': ['World/Quests/MythicQuests/Angel/**/*.jbp'],
        'Act/Quest/Mythic/Azata': ['World/Quests/MythicQuests/Azata/**/*.jbp'],
        'Act/Quest/Mythic/Demon': ['World/Quests/MythicQuests/Demon/**/*.jbp'],
        'Act/Quest/Mythic/Devil': ['World/Quests/MythicQuests/Devil/**/*.jbp'],
        'Act/Quest/Mythic/Dragon': ['World/Quests/MythicQuests/Dragon/**/*.jbp'],
        'Act/Quest/Mythic/Legend': ['World/Quests/MythicQuests/Legend/**/*.jbp'],
        'Act/Quest/Mythic/Lich': ['World/Quests/MythicQuests/Lich/**/*.jbp'],
        'Act/Quest/Mythic/Swarm': ['World/Quests/MythicQuests/Locust/**/*.jbp'],
        'Act/Quest/Mythic/Trickster': ['World/Quests/MythicQuests/Trickster/**/*.jbp'],
        'Crusade/Relics/Act_2': ['World/Crusade/Events/Relics/Ch2/*.jbp'],
        'Crusade/Relics/Act_3': ['World/Crusade/Events/Relics/Ch3/*.jbp'],
        'Crusade/Relics/Act_4': ['World/Crusade/Events/Relics/Ch4/*.jbp'],
        'Crusade/Relics/Act_5': ['World/Crusade/Events/Relics/Ch5/*.jbp'],
        'Crusade/RankUp/Diplomacy': ['World/Crusade/RankUps/Diplomacy/**/*.jbp'],
        'Crusade/RankUp/Leadership': ['World/Crusade/RankUps/Leadership/**/*.jbp'],
        'Crusade/RankUp/Logistic': ['World/Crusade/RankUps/Logistics/**/*.jbp'],
        'Crusade/RankUp/Military': ['World/Crusade/RankUps/Military/**/*.jbp'],
        'Crusade/RankUp/Mythic/Aeon': ['World/Crusade/RankUps/MythicRankUps/Aeon/**/*.jbp'],
        'Crusade/RankUp/Mythic/Angel': ['World/Crusade/RankUps/MythicRankUps/Angel/**/*.jbp'],
        'Crusade/RankUp/Mythic/Azata': ['World/Crusade/RankUps/MythicRankUps/Azata/**/*.jbp'],
        'Crusade/RankUp/Mythic/Demon': ['World/Crusade/RankUps/MythicRankUps/Demon/**/*.jbp'],
        'Crusade/RankUp/Mythic/Dragon': ['World/Crusade/RankUps/MythicRankUps/Dragon/**/*.jbp'],
        'Crusade/RankUp/Mythic/Legend': ['World/Crusade/RankUps/MythicRankUps/Legend/**/*.jbp'],
        'Crusade/RankUp/Mythic/Lich': ['World/Crusade/RankUps/MythicRankUps/Lich/**/*.jbp'],
        'Crusade/RankUp/Mythic/Swarm': ['World/Crusade/RankUps/MythicRankUps/Locust/**/*.jbp'],
        'Crusade/RankUp/Mythic/Trickster': ['World/Crusade/RankUps/MythicRankUps/Trickster/**/*.jbp'],
        'Crusade/Items': ['World/Crusade/CrusadeItems/**/*.jbp'],
        'Crusade/Army': ['World/Crusade/CrusadeArmy/**/*.jbp'],
        'Crusade/Quests': ['World/Quests/Crusade/**/*.jbp'],
    }

    addSubdirToFilterList(filters, 'Spells')
    addSubdirToFilterList(filters, 'Feats')
    addSubdirToFilterList(filters, 'Classes')
    addSubdirToFilterList(filters, 'Equipment')
    addSubdirToFilterList(filters, 'Items')
    addSubdirToFilterList(filters, 'Armies')
    addSubdirToFilterList(filters, 'Units')
    addSubdirToFilterList(filters, 'Weapons/Items')
    addSubdirToFilterList(filters, 'Weapons')
    addSubdirToFilterList(filters, 'World')

    for f in zip.namelist():
        if f.count('/') != 1 or not f.endswith('/'):
            continue
        filters[f[:-1]] = [f'{f}**/*.jbp', f'{f}*.jbp']

    futures = {
        k: pool.submit(filter_by_pattern,  filters[k]) for k in filters
    }

    results = OrderedDict()
    results['Shared/Location'] = list(set([
        *searchStringKey("**/Location*.jbp", "Name"),
        *searchStringKey("**/*.jbp", "AreaName")
    ]))
    results['Shared/Duration'] = searchStringKey(
        "**/*.jbp", "LocalizedDuration")
    results['Shared/SavingThrow'] = searchStringKey(
        "**/*.jbp", "LocalizedSavingThrow")
    results['Shared/ToolTip'] = searchStringKey(
        "**/*.jbp", "m_Tooltip")
    results["Shared/BattleLog"] = searchStringKey(
        "**/*.jbp", "CustomBattlelogMessage")
    results['Shared/DisplayName'] = searchStringKey(
        "**/*.jbp", "DisplayNameText")

    for k in futures.keys():
        results[k] = futures[k].result()

    keySet = set()
    for k in results:
        results[k] = [x for x in results[k] if x not in keySet]
        keySet.update(results[k])

    for fname in results:
        r_en = {x: en[x] for x in results[fname] if x in en}
        r_kr = {x: kr[x] for x in results[fname] if x in kr}
        for k in r_en:
            if k not in r_kr:
                r_kr[k] = r_en[k]
        writeOrUnlink(r_en, Path("patches", f"{fname}-en.json"))
        writeOrUnlink(r_kr, Path("patches", f"{fname}-kr.json"))

    missing = set(en.keys()) - keySet
    missing_en = {x: en[x] for x in missing}
    missing_kr = {x: kr[x] for x in missing if x in kr}
    for k in missing_en:
        if k not in missing_kr:
            missing_kr[k] = missing_en[k]
    writeOrUnlink(missing_en, Path("patches", f"missing-en.json"))
    writeOrUnlink(missing_kr, Path("patches", f"missing-kr.json"))
