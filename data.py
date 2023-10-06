from glob import glob
import zipfile

import utils

_data_en = None
_data_kr = None
_data_bp = None


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
        _data_bp = zipfile.ZipFile("./blueprints.zip")
    return _data_bp


def get_data_kr_patches():
    kr = {}
    for f in glob('patches/*-kr.json'):
        kr.update(utils.read_json(f))
    return kr
