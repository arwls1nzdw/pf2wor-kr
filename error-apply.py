from glob import glob
from pathlib import Path

import utils

last_modified = None
for f in Path().glob('./errors.json'):
    if last_modified is None or f.stat().st_mtime > last_modified.stat().st_mtime:
        last_modified = f

if last_modified is None:
    raise Exception('No error files found.')

print(f'Using {last_modified} as error data')
errors_data = utils.read_json(last_modified)

for kr in glob('patches/**/*-kr.json', recursive=True):
    kr_data = utils.read_json(kr)
    for key, value in errors_data.items():
        if key in kr_data:
            kr_data[key] = value['kr']
    utils.write_json(kr_data, kr)
