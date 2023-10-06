import fnmatch
import json
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
            print_path_of_val(data, val, *prev_paths, key)
            yield val


keySet = set()


def filter_by_pattern(*patterns):
    global keySet, zip
    print("filter_by_pattern", patterns)
    ret = set()
    for p in patterns:
        ret.update(
            seq(fnmatch.filter(zip.namelist(), p))
            .map(lambda p: zip.read(p).decode('utf-8'))
            .map(lambda d: json.loads(d))
            .map(find_string_keys)
            .map(list)
            .flatten()
            .filter(lambda k: k not in keySet)
            .to_set()
        )
        keySet.update(ret)
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

# filters = {
#     'feats': partial(filter_by_pattern, 'Feats/**/*.jbp'),
#     'spells': partial(filter_by_pattern, 'Spells/**/*.jbp'),
#     'crusade': partial(filter_by_pattern, 'Armies/**/*.jbp', 'Kingdom/**/*.jbp', "**/Crusade/**/*.jbp"),
#     'mythics': partial(filter_by_pattern, 'Mythic/**/*.jbp'),
#     'encyclopedia': partial(filter_by_pattern, 'Encyclopedia/**/*.jbp'),
#     'archivements': partial(filter_by_pattern, 'Archivements/**/*.jbp'),
#     'character': partial(filter_by_pattern, 'Traits/**/*.jbp', 'Backgrounds/**/*.jbp'),
#     'class': partial(filter_by_pattern, 'Classes/**/*.jbp', 'ClassGroups/**/*.jbp'),
#     'items': partial(filter_by_pattern,
#         'Items/**/*.jbp',
#         'Equipment/**/*.jbp',
#         'Recipes/**/*.jbp',
#         'Weapons/**/*.jbp',
#     ),
#     'ui': partial(filter_by_pattern, 'UI/**/*.jbp', 'Sounds/**/*.jbp'),
# }


# 가장 나중에 필터링
last_filters = ['QA', 'Test', 'Sound', ]

rootdirs = seq(zip.filelist) \
    .filter(lambda f: f.filename.endswith('/') and f.filename.count('/') == 1) \
    .map(lambda f: f.filename[:-1]) \
    .sorted(key=lambda d: 'Z' if d in last_filters else d) \
    .to_list()

filters = {
    "Spells": partial(filter_by_pattern, 'Spells/**/*.jbp'),
    "Feats": partial(filter_by_pattern, 'Feats/**/*.jbp'),
    "Classes": partial(filter_by_pattern, 'Classes/**/*.jbp'),
    "Mythic": partial(filter_by_pattern, 'Mythic/**/*.jbp'),
    "Armies": partial(filter_by_pattern, 'Armies/**/*.jbp'),
    "Units": partial(filter_by_pattern, 'Units/**/*.jbp'),
    "Items": partial(filter_by_pattern, 'Items/**/*.jbp'),
}
filters = {
    **filters,
    **{d: partial(filter_by_pattern, f'{d}/**/*.jbp') for d in rootdirs if d not in filters}
}

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
    dump_with_sort(f'patches/{name}-en.json', out_en)
    dump_with_sort(f'patches/{name}-kr.json', out_kr)

print("=======summary=======")
for key in sorted(data.keys(), key=lambda d: len(data[d])):
    if len(data[key]) == 0:
        continue
    print(f"{key:20s}: {len(data[key]):>6,}({len(data[key]) / len(en) * 100:.2f}%)")
