from glob import glob

import utils

diff = utils.read_json("diff.json")

for f in glob("patches/**/*-kr.json", recursive=True):
    data = utils.read_json(f)
    for key in data:
        if key not in diff:
            continue
        data[key] = diff[key][2]

    utils.write_json(data, f)

print(len(diff))
