from LARGE_FIRES_visuals import large_fires
from collections import Counter
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np


plt.style.use('seaborn')

# Global JSON data files
with open('data/Fires_Northwest.json') as e:
    fires = json.load(e)

human_count = 0
ltng_count = 0
human_acres = 0
ltng_acres =0

for fire in fires:
    #human
    if fire['STAT_CAUSE'] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
        human_count += 1
        human_acres += fire['SIZE_AC']
    # lightning
    if fire['STAT_CAUSE'] == 1:
        ltng_count += 1
        ltng_acres += fire['SIZE_AC']

human_perc_occ = human_count / (human_count + ltng_count)
human_perc_burned = human_acres / (human_acres + ltng_acres)
ltng_perc_occ = ltng_count / (human_count + ltng_count)
ltng_perc_burned = ltng_acres / (human_acres + ltng_acres)
print(human_perc_occ, human_perc_burned,  ltng_perc_occ, ltng_perc_burned)

########################################################################################################################
# YEAR FREQUENCY OF FIRES                                                                                              #
########################################################################################################################
def fires_by_year(fires):
    years = []
    for fire in fires:
        years.append(str(fire['DISC_DATE'])[:4])
    year_count = Counter(years)
    print(year_count)
    # plt.scatter(year_count.keys(), year_count.values(), edgecolor='black', linewidth=1.0)
    # plt.title("Frequency of Fires by Year")
    # plt.ylabel("Number of Fires")
    # plt.xlabel("Year")
    # plt.savefig('graphics/fires_by_year.png', dpi=600)
    # plt.show()
    return year_count

# years = fires_by_year(fires)

########################################################################################################################
# MONTH FREQUENCY OF FIRES                                                                                             #
########################################################################################################################
def fires_by_month(fires, years, largefires):
    months = []
    lf_months = []
    lf_years = []
    acres_in = 0
    acres_out = 0
    for fire in fires:
        months.append(str(fire['DISC_DATE'])[4:6])
        if str(fire['DISC_DATE'])[4:6] in ['06', '07', '08', '09', '10']:
            acres_in += fire['SIZE_AC']
        else:
            acres_out += fire['SIZE_AC']

    for lf in largefires:
        lf_months.append(str(lf['DISC_DATE'])[4:6])

    for lf in largefires:
        lf_years.append(str(lf['DISC_DATE'])[:4])

    month_count = Counter(sorted(months))
    lf_count = Counter(sorted(lf_months))
    lf_year_count = Counter(lf_years)

    causes = []
    for fire in fires:
        if fire['STAT_CAUSE'] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            causes.append('Human')
        elif fire['STAT_CAUSE'] == 1:
            causes.append('Lightning')
        elif fire['STAT_CAUSE'] == 13:
            causes.append('Missing')

    cause_count = Counter(sorted(causes))


    lf_causes = []
    for lf in largefires:
        if lf['STAT_CAUSE'] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
            lf_causes.append('Human')
        elif lf['STAT_CAUSE'] == 1:
            lf_causes.append('Lightning')
        elif lf['STAT_CAUSE'] == 13:
            lf_causes.append('Missing')

    lf_cause_count = Counter(sorted(lf_causes))

    forest = []
    for fire in fires:
        if fire['FORESTED'] == 'yes':
            forest.append('Forested')
        else:
            forest.append('Non-Forested')
    forest_count = Counter(forest)

    lf_forest = []
    for lf in largefires:
        if lf['FORESTED'] == 'yes':
            lf_forest.append('Forested')
        else:
            lf_forest.append('Non-Forested')
    lf_forest_count = Counter(lf_forest)

    fig = plt.figure(figsize=(8.5, 10))

    ax0 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
    ax1 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)

    ax0.bar(sorted(years.keys()), years.values(), label='All Fires')
    ax0.bar(sorted(lf_year_count.keys()), lf_year_count.values(), label='90th Percentile Fires')
    ax0.set_yscale('log')
    ax0.title.set_text('(a) Occurrence Year')
    ax0.set_xlabel('Year')
    ax0.set_ylim(10, 100000)

    for tick in ax0.get_xticklabels():
        tick.set_fontsize(8)    
    for tick in ax0.get_yticklabels():
        tick.set_fontsize(8)   

    ax1.bar(month_count.keys(), month_count.values(), label='All Fires')
    ax1.bar(lf_count.keys(), lf_count.values(), label='90th Percentile Fires')
    ax1.set_yscale('log')
    ax1.set_xlabel('Month')
    ax1.title.set_text('(b) Occurrence Month')
    ax1.set_ylim(10, 100000)

    for tick in ax1.get_xticklabels():
        tick.set_fontsize(8)    
    for tick in ax1.get_yticklabels():
        tick.set_fontsize(8)   

    ax2.bar(cause_count.keys(), cause_count.values(), label='All Fires')
    ax2.bar(lf_cause_count.keys(), lf_cause_count.values(), label='90th Percentile Fires')
    ax2.set_yscale('log')
    ax2.set_xlabel('Cause')
    ax2.title.set_text('(c) Ignition Cause')
    ax2.set_ylim(10, 100000)

    for tick in ax2.get_xticklabels():
        tick.set_fontsize(8)    
    for tick in ax2.get_yticklabels():
        tick.set_fontsize(8)   

    ax3.bar(forest_count.keys(), forest_count.values(), label='All Fires')
    ax3.bar(lf_forest_count.keys(), lf_forest_count.values(), label='90th Percentile Fires')
    ax3.set_yscale('log')
    ax3.set_xlabel('Forest Type')
    ax3.title.set_text('(d) Forested / Non-Forested')
    ax3.set_ylim(10, 100000)

    for tick in ax3.get_xticklabels():
        tick.set_fontsize(8)    
    for tick in ax3.get_yticklabels():
        tick.set_fontsize(8)   

    handles, labels = ax3.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center')
    plt.subplots_adjust(left=0.10, right=0.99, top=0.88, hspace=0.3)
    fig.text(0.03, 0.75, 'Number of Fires\nLg(x)', ha='center', va='center', rotation='vertical')
    fig.text(0.03, 0.30, 'Number of Fires\nLg(x)', ha='center', va='center', rotation='vertical')
    fig.text(0.1, 0.96, 'Characteristics of Fires in the Northwestern U.S.\n(2006 - 2015) n = 64,122', ha='left', va='center', fontsize=16)
    plt.savefig('graphics/fires_mega_plot.png', dpi=600)
    # plt.tight_layout()
    plt.show()
 
# fires_by_month(fires, years, large_fires)

########################################################################################################################
# FIRE FREQUENCY BY CAUSE                                                                                              #
########################################################################################################################
def fires_by_cause(fires):
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
    plt.savefig('graphics/fires_by_cause.png', dpi=600)
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
    plt.savefig('graphics/fires_by_wfo.png', dpi=600)
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
    plt.savefig('graphics/fires_by_forest.png', dpi=600)
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
    plt.savefig('graphics/fires_by_avg_size.png', dpi=600)
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
    plt.savefig('graphics/fires_by_90thsize.png', dpi=600)
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
    plt.savefig('graphics/fires_by_size_90th_erc.png', dpi=600)

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
