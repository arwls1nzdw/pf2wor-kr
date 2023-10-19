import json
import sys
from glob import glob


group = sys.argv[1].capitalize() if len(sys.argv) > 1 else "**"

total = 0
summary = []
max_namelen = 0
max_datalen = 0
sum_datalen = 0
for f in glob(f"patches/{group}/*-kr.json", recursive=True):
    d = json.load(open(f, 'r', encoding='utf-8'))
    summary.append((f, len(d)))
    total += len(d)
    max_namelen = max(max_namelen, len(f))
    max_datalen = max(max_datalen, len(str(len(d))))
    sum_datalen += len(d)

summary.sort(key=lambda x: x[1])

for s in summary:
    print(f"{s[0]:<{max_namelen}} {s[1]:{max_datalen}d} ({s[1]/total*100:.2f}%)")

print("")
print(f"total: {total}, avg: {sum_datalen/len(summary):.2f}")
