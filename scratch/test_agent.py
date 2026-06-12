import sys
sys.path.insert(0, ".")
from agents.disaster_ai import detect_disaster_type, detect_location, _gmaps_url

queries = [
    "earthquake in delhi",
    "cyclone in bhubaneswar",
    "fire in chennai",
    "gas leak in bhopal",
    "flood in patna",
]

for q in queries:
    t = detect_disaster_type(q)
    c, l, d = detect_location(q)
    sz = d["safe_zone"]
    ev = d["evac_dir"]
    gm = _gmaps_url(d["safe_lat"], d["safe_lon"])
    print(f"  {t:20s} | {l:15s} | {sz:40s} | {ev}")
    print(f"  {'':20s} | {'':15s} | Maps: {gm}")
    print()
