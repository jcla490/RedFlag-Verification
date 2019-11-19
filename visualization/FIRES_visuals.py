from collections import Counter
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np

# Global JSON data files
with open('data/Fires_Northwest.json') as e:
    fires = json.load(e)

########################################################################################################################
# YEAR FREQUENCY OF FIRES                                                                                              #
########################################################################################################################
def fires_by_year(fires):
    years = []
    for fire in fires:
        years.append(str(fire['DISC_DATE'])[:4])
    year_count = Counter(years)
    print(year_count)
    plt.scatter(year_count.keys(), year_count.values(), edgecolor='black', linewidth=1.0)
    plt.title("Frequency of Fires by Year")
    plt.ylabel("Number of Fires")
    plt.xlabel("Year")
    plt.show()

fires_by_year(fires)

########################################################################################################################
# MONTH FREQUENCY OF FIRES                                                                                             #
########################################################################################################################
def fires_by_month(fires):
    months = []
    for fire in fires:
        months.append(str(fire['DISC_DATE'])[4:6])
    month_count = Counter(sorted(months))
    print(month_count)
    fig = plt.figure(figsize=(8, 3))
    ax0 = plt.subplot2grid((1, 3), (0, 0), colspan=2)
    ax1 = plt.subplot2grid((1, 3), (0, 2))

    ax0.bar(month_count.keys(), month_count.values(), color='#337CBA', edgecolor='black', linewidth=1.0, width=1)
    # plt.title("Frequency of Fires by Month")
    ax0.set_ylabel("Number of Fires", fontname='Helvetica Neue')
    ax0.set_xlabel("Month", fontname='Helvetica Neue')
    ax0.title.set_text('(a) Fires by Month')

    causes = []
    for fire in fires:
        if fire['STAT_CAUSE'] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            causes.append('Human')
        elif fire['STAT_CAUSE'] == 1:
            causes.append('Lightning')
        elif fire['STAT_CAUSE'] == 13:
            causes.append('Missing')

    month_count = Counter(sorted(causes))
    print(month_count)
    print(list(month_count.keys()))
    ax1.bar(month_count.keys(), month_count.values(), color='#337CBA', edgecolor='black', linewidth=1.0, width=1)
    # plt.title("Frequency of Fires by Month")
    # axs[1].set_ylabel("Causes")
    ax1.set_xlabel("Cause", fontname='Helvetica Neue')
    ax1.title.set_text('(b) Fires by Cause Type')

    for tick in ax1.get_xticklabels():
        tick.set_fontname("Helvetica Neue")
    for tick in ax1.get_yticklabels():
        tick.set_fontname("Helvetica Neue")
    for tick in ax0.get_xticklabels():
        tick.set_fontname("Helvetica Neue")
    for tick in ax0.get_yticklabels():
        tick.set_fontname("Helvetica Neue")

    plt.tight_layout()
    plt.savefig('fires_graph.png', dpi=600)

fires_by_month(fires)

def fires_by_cause(fires):
    ltng_codes = ['1']
    human_codes = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    causes = []
    for fire in fires:
        if fire['STAT_CAUSE'] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            causes.append('Human')
        elif fire['STAT_CAUSE'] == 1:
            causes.append('Lightning')
        elif fire['STAT_CAUSE'] == 13:
            causes.append('Missing/Undefined')

    month_count = Counter(sorted(causes))
    print(month_count)
    plt.bar(month_count.keys(), month_count.values(), edgecolor='black', linewidth=1.0, width=1)
    # plt.title("Frequency of Fires by Month")
    plt.ylabel("Number of Fires")
    plt.xlabel("Cause Type", fontsize=14)
    plt.show()

# fires_by_cause(fires)

########################################################################################################################
# FIRE FREQUENCY BY WFO                                                                                                #
########################################################################################################################
def fires_by_wfo(fires):
    office = []
    for fire in fires:
        office.append(fire['WFO'])
    office_count = Counter(office)
    print(office_count)
    plt.bar(office_count.keys(), office_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of Fires by Office")
    plt.ylabel("Number of Fires")
    plt.xlabel("Office")
    plt.show()

# fires_by_wfo(fires)

########################################################################################################################
# FIRE FREQUENCY BY ZONE                                                                                               #
########################################################################################################################
def fires_by_zone(fires):
    zones = []
    for fire in fires:
        zones.append(fire['UGC_ZONE'])
    zone_count = Counter(zones)
    print(zone_count)
    plt.bar(zone_count.keys(), zone_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of Fires by Zone")
    plt.ylabel("Number of Fires")
    plt.xlabel("Zone")
    plt.show()

# fires_by_zone(fires)

########################################################################################################################
# FIRE FREQUENCY BY FOREST COVER                                                                                       #
########################################################################################################################
def fires_by_forest(fires):
    forest = []
    for fire in fires:
        if fire['FORESTED'] == 'yes':
            forest.append(fire['WFO'])
    forest_count = Counter(forest)
    print(forest_count)
    plt.bar(forest_count.keys(), forest_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of Fires Classified as Forested")
    plt.ylabel("Number of Fires")
    plt.xlabel("Office")
    plt.show()

# fires_by_forest(fires)

########################################################################################################################
# AVG SIZES FOR FIRES IN WFO                                                                                           #
########################################################################################################################
def fires_avg_size(fires):
    sizes_dict ={}
    wfos = ['SEW', 'PQR', 'MFR', 'PDT', 'BOI', 'OTX', 'PIH', 'MSO']
    for wfo in wfos:
        avg_sizes = []
        for fire in fires:
            if fire['WFO'] == wfo:
                avg_sizes.append(fire['SIZE_AC'])
        sizes_dict[wfo] = sum(avg_sizes)/len(avg_sizes)
    print(sizes_dict)

    plt.bar(sizes_dict.keys(), sizes_dict.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Average Fire Size by WFO")
    plt.ylabel("Average Size of Fires")
    plt.xlabel("Office")
    plt.show()

# fires_avg_size(fires)

########################################################################################################################
# 90th PERCENTILE SIZES FOR FIRES IN WFO                                                                               #
########################################################################################################################
def fires_90_size(fires):
    sizes_dict ={}
    wfos = ['SEW', 'PQR', 'MFR', 'PDT', 'BOI', 'OTX', 'PIH', 'MSO']
    for wfo in wfos:
        avg_sizes = []
        for fire in fires:
            if fire['WFO'] == wfo:
                avg_sizes.append(fire['SIZE_AC'])
        sizes_dict[wfo] = np.percentile(avg_sizes, 90)
    print(sizes_dict)

    plt.bar(sizes_dict.keys(), sizes_dict.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("90th Percentile Fire Sizes by WFO")
    plt.ylabel("90th Percentile Size of Fires")
    plt.xlabel("Office")
    plt.show()

# fires_90_size(fires)

########################################################################################################################
# AVG SIZE WHEN ERC ABOVE 90TH PERCENTILE                                                                              #
########################################################################################################################
def fires_size_erc_perc(fires):
    sizes_dict ={}
    wfos = ['SEW', 'PQR', 'MFR', 'PDT', 'BOI', 'OTX', 'PIH', 'MSO']
    for wfo in wfos:
        avg_sizes = []
        for fire in fires:
            if fire['WFO'] == wfo:
                if fire['ERC_PERC'] >= 85:
                    avg_sizes.append(fire['SIZE_AC'])
        sizes_dict[wfo] = sum(avg_sizes)/len(avg_sizes)
    print(sizes_dict)

    plt.bar(sizes_dict.keys(), sizes_dict.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Average Size when ERC >= 90th Percentile by WFO")
    plt.ylabel("Average Size")
    plt.xlabel("Office")
    plt.show()

# fires_size_erc_perc(fires)

# what is probability a fire in August with an ERC above 85th percentile will exceed 10 ac size in WAZ687

def waz687_prob(fires):
    fire_hits = []
    fire_nums = []
    for fire in fires:
        if fire['UGC_ZONE'] == 'WAZ687':
            if str(fire['DISC_DATE'])[4:6] == '08':
                if fire['ERC_PERC'] >= 95:
                    if fire['BI_PERC'] >= 80:
                        if fire['SIZE_AC'] >= 1000:
                            fire_hits.append(fire['ID'])
                        else:
                            fire_nums.append(fire['ID'])

    print(len(fire_hits) / (len(fire_hits) + len(fire_nums)))

# waz687_prob(fires)

#what is actually wrong