from collections import Counter
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np

# Global JSON data files
with open('data/Fires_Northwest.json') as e:
    fires = json.load(e)


def large_fires_sizer(fires, perc_input):
    zone_sizes = {}
    for fire in fires:
        if fire['UGC_ZONE'] in zone_sizes:
            zone_sizes[fire['UGC_ZONE']].append(fire['SIZE_AC'])
        else:
            zone_sizes[fire['UGC_ZONE']] = [fire['SIZE_AC']]

    perc_list = []
    for k, v in zone_sizes.items():
        m = np.array(v)
        p = round(np.percentile(m, perc_input), 2)
        perc_list.append({k: p})

    print(str(perc_input) + 'th percentile fire sizes for the zones requested are:', perc_list)
    return perc_list

# Pass in fires JSON and a percentile size and watch your large fires come to life!
fire_sizes = large_fires_sizer(fires, 90)

def large_fires_counter(fires, fire_sizes):
    large_fires = []
    for fire in fires:
        for size in fire_sizes:
            if fire['UGC_ZONE'] in size:
                if fire['SIZE_AC'] >= size[fire['UGC_ZONE']]:
                    large_fires.append(fire)

    print(len(large_fires))
    return large_fires

large_fires = large_fires_counter(fires, fire_sizes)