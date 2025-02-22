import glob
import json
import os

names = glob.glob("./tickers/*.json")
to_fix = []

for path in names:
    with open(path) as file:
        try:
            json.load(file)
        except Exception:
            to_fix.append(os.path.splitext(os.path.basename(path))[0])

for name in to_fix:
    with open(f"./tickers/{name}.json", "w") as file:
        json.dump([{"symbol": name, "__fetch_time": "2025-02-21"}], file)

print(to_fix)
