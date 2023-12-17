import fnmatch
from collections import defaultdict
from pathlib import Path

import utils


def isDummy(text: str):
    if len(text) == 0:
        return True
    if "[draft]" in text.lower():
        return True
    return False


def find_all_stringKeys(data, *prev_paths):
    iter = data
    if isinstance(data, list):
        iter = [i for i in range(len(data))]

    for key in iter:
        val = data[key]

        if not isinstance(val, str) and (hasattr(val, '__iter__') or hasattr(val, '__getitem__')):
            yield from find_all_stringKeys(val, *prev_paths, key)
        if isinstance(val, str) and val in enGB:
            yield val
        if isinstance(key, str) and key in enGB:
            yield key


def searchStringKey(filelist, jbpFilePattern, *jsonPaths):
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
            elif all(map(lambda p: p in prev_paths, jsonPaths)) and val in enGB:
                yield val

    matches = set(fnmatch.filter(filelist, jbpFilePattern))
    ret = set()
    for match in matches:
        json_data = bp.read_json(match)
        inner_data = inner(json_data)
        for item in inner_data:
            ret.add(item)
    return ret


if __name__ == "__main__":
    import dataloader

    bp = dataloader.get_data_bp()
    enGB = utils.read_json("dist/enGB.json")['strings']
    koKR = utils.read_json("dist/koKR.json")['strings']

    dummyKeys = [k for k in enGB if isDummy(enGB[k])]
    for k in dummyKeys:
        del enGB[k]
        if k in koKR:
            del koKR[k]

    filelist = bp.filelist
    filelist = map(lambda f: f.filename, filelist)
    filelist = map(lambda f: f.replace("\\", "/"), filelist)
    filelist = list(filelist)

    def getSubGroups(rootGroup, depth):
        if depth == 0:
            return set([rootGroup])

        if depth == 1:
            iter = fnmatch.filter(filelist, f"{rootGroup}/*")
        else:
            iter = fnmatch.filter(filelist, f"{rootGroup}/**/*")

        subGroups = set()
        for f in iter:
            if not f.endswith('/'):
                continue

            if f.count('/') == depth + rootGroup.count('/') + 1:
                groupKey = '/'.join(f.split("/"))
                if groupKey.endswith('/'):
                    groupKey = groupKey[:-1]
                subGroups.add(groupKey)
        return subGroups

    groupNames = set()
    groupNames.update([f[:-1] for f in filelist if f.count('/') == 1 and f.endswith('/')])
    groupNames.update(getSubGroups("Armies", 1))
    groupNames.update(getSubGroups("Buffs", 1))
    groupNames.update(getSubGroups("Classes", 1))
    groupNames.update(getSubGroups("Equipment", 1))
    groupNames.update(getSubGroups("Feats", 1))
    groupNames.update(getSubGroups("Items", 1))
    groupNames.update(getSubGroups("Mythic", 1))
    groupNames.update(getSubGroups("Root", 1))
    groupNames.update(getSubGroups("Spells", 1))
    groupNames.update(getSubGroups("Units", 1))
    groupNames.update(getSubGroups("Weapons", 1))
    groupNames.update(getSubGroups("World", 1))
    groupNames.update(getSubGroups("World/Dialogs", 1))
    groupNames.update(getSubGroups("World/Dialogs/Companions", 2))
    groupNames.update(getSubGroups("World/Quests", 1))
    groupNames.update(getSubGroups("World/Quests/Companions", 1))
    groupNames.update(getSubGroups("World/Quests/MythicQuests", 1))
    groupNames = sorted(groupNames)

    grouped = defaultdict(set)
    current = defaultdict(lambda: None)
    for f in filelist:
        if f.endswith('/'):
            continue

        for g in groupNames:
            if f.startswith(f"{g}/"):
                if any(map(lambda x: x.startswith(f"{g}/") and x.count('/') > g.count('/'), groupNames)):
                    g = f"{g}/_others"
                grouped[g].add(f)
                if current[f]:
                    grouped[current[f]].remove(f)
                current[f] = g

    grouped_stringKeys = defaultdict(set)
    for g in grouped:
        output = defaultdict(dict)
        for f in grouped[g]:
            bpData: dict = bp.read_json(f)
            grouped_stringKeys[g].update(find_all_stringKeys(bpData))

    keyFound = set()
    current = defaultdict(set)
    grouped_stringKeys['Shared/Duration'] = searchStringKey(filelist, "**/*.jbp", "LocalizedDuration")
    grouped_stringKeys['Shared/SavingThrow'] = searchStringKey(filelist, "**/*.jbp", "LocalizedSavingThrow")
    for g in grouped_stringKeys:
        for k in grouped_stringKeys[g]:
            if current[k]:
                grouped_stringKeys[current[k]].remove(k)
            current[k] = g
            keyFound.add(k)

    for g in grouped_stringKeys:
        output = {
            'en': {},
            'kr': {}
        }
        for k in grouped_stringKeys[g]:
            output["en"][k] = enGB[k]
            output["kr"][k] = koKR[k] if k in koKR else enGB[k]

        if len(output["en"]) == 0:
            continue

        output["en"] = dict(sorted(output["en"].items(), key=lambda x: (enGB[x[0]], x[0])))
        output["kr"] = dict(sorted(output["kr"].items(), key=lambda x: (enGB[x[0]], x[0])))

        utils.write_json(output["en"], f"patches/{g}-en.json")
        utils.write_json(output["kr"], f"patches/{g}-kr.json")

    missingData = defaultdict(dict)
    for k in [k for k in enGB if k not in keyFound]:
        missingData['en'][k] = enGB[k]
        missingData['kr'][k] = koKR[k]

    missingData['en'] = dict(sorted(missingData['en'].items(), key=lambda x: (enGB[x[0]], x[0])))
    missingData['kr'] = dict(sorted(missingData['kr'].items(), key=lambda x: (enGB[x[0]], x[0])))
    utils.write_json(missingData['en'], "patches/missing-en.json")
    utils.write_json(missingData['kr'], "patches/missing-kr.json")
