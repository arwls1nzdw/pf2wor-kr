from glob import glob
import json
from pathlib import Path
import zipfile

import utils


class CachedZipFile(zipfile.ZipFile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def read(self, name, pwd=None):
        data = super().read(name, pwd)
        self._cache[name] = data
        return data

    def read_json(self, name):
        return json.loads(self.read(name).decode('utf-8'))


_data_en: dict = None
_data_kr: dict = None
_data_bp: CachedZipFile = None


def get_data_en():
    global _data_en
    if _data_en is None:
        _data_en = utils.read_json('dist/enGB.json')
    return _data_en


def get_data_kr():
    global _data_kr
    if _data_kr is None:
        _data_kr = utils.read_json('dist/koKR.json')
    return _data_kr


def get_data_bp():
    global _data_bp
    if _data_bp is None:
        _data_bp = CachedZipFile("./blueprints.zip")
    return _data_bp


def get_data_kr_patches():
    kr = {}
    for f in glob('patches/*-kr.json'):
        if Path(f).stem == 'Owlcats-kr':
            continue
        kr.update(utils.read_json(f))
    return kr
