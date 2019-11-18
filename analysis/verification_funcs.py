from datetime import datetime, timedelta
import numpy as np
import random
import json

# Global JSON data files
with open('../Data/RFWs_Northwest.json') as e:
    rfws = json.load(e)

with open('../Data/Fires_Northwest.json') as f:
    fires = json.load(f)

print(len(rfws), len(fires))

def verify(startdate, enddate, **kwargs):

    if 'wfo' in kwargs:
        rfws_clip = [rfw for rfw in rfws if rfw['WFO'] == kwargs['wfo']]
        fires_clip = [fire for fire in fires if fire['WFO'] == kwargs['wfo']]
    else:
        rfws_clip = rfws
        fires_clip = fires

    if 'zone' in kwargs:
        rfws_clip = [rfw for rfw in rfws_clip if rfw['NWS_UGC'] == kwargs['zone']]
        fires_clip = [fire for fire in fires_clip if fire['UGC_ZONE'] == kwargs['zone']]

    if 'cause' in kwargs:
        if kwargs['cause'] == 'lightning':
            ltng_codes = ['1']
            fires_clip = [fire for fire in fires_clip if str(fire['STAT_CAUSE']) in ltng_codes]

        if kwargs['cause'] == 'human':
            human_codes = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
            fires_clip = [fire for fire in fires_clip if str(fire['STAT_CAUSE']) in human_codes]

    if 'forestcover' in kwargs:
        fires_clip = [fire for fire in fires_clip if fire['FORESTED'] == kwargs['forestcover']]

    if 'nfdrs_param' in kwargs:
        fd_index, fd_operator, fd_threshold = kwargs['nfdrs_param'][0], kwargs['nfdrs_param'][1], kwargs['nfdrs_param'][2]
        if fd_operator == '<=':
            fires_clip = [fire for fire in fires_clip if fire[fd_index] <= fd_threshold]
        elif fd_operator == '==':
            fires_clip = [fire for fire in fires_clip if fire[fd_index] == fd_threshold]
        elif fd_operator == '>=':
            fires_clip = [fire for fire in fires_clip if fire[fd_index] >= fd_threshold]

    fires_clip = [fire for fire in fires_clip if datetime.strptime(str(startdate), '%Y%m%d') <=
                  datetime.strptime(str(fire['DISC_DATE'])[:8], '%Y%m%d') <= datetime.strptime(str(enddate), '%Y%m%d')]
    rfws_clip = [rfw for rfw in rfws_clip if datetime.strptime(str(startdate), '%Y%m%d') <=
                 datetime.strptime(rfw['FLAT_DATE'], '%Y%m%d') <= datetime.strptime(str(enddate), '%Y%m%d')]

    if 'duration' in kwargs:
        rfws_dummy = []
        for rfw in rfws_clip:
            start = rfw['ISSUED']
            end = rfw['EXPIRED']
            start_datetime = datetime.strptime(start, "%Y%m%d%H%M")
            end_datetime = datetime.strptime(end, "%Y%m%d%H%M")
            hours = (end_datetime - start_datetime).seconds / 3600
            if kwargs['duration'] == 6:
                if 0 <= hours <= 6:
                    rfws_dummy.append(rfw)
            elif kwargs['duration'] == 12:
                if 6 < hours <= 12:
                    rfws_dummy.append(rfw)
            elif kwargs['duration'] == 18:
                if 12 < hours <= 18:
                    rfws_dummy.append(rfw)
            elif kwargs['duration'] == 24:
                if 18 < hours <= 24:
                    rfws_dummy.append(rfw)
        rfws_clip = rfws_dummy

    if 'perc_size' in kwargs:
        zone_sizes = {}
        for fire in fires_clip:
            if fire['UGC_ZONE'] in zone_sizes:
                zone_sizes[fire['UGC_ZONE']].append(fire['SIZE_AC'])
            else:
                zone_sizes[fire['UGC_ZONE']] = [fire['SIZE_AC']]

        perc_list = []
        for k, v in zone_sizes.items():
            m = np.array(v)
            p = round(np.percentile(m, kwargs['perc_size']), 2)
            perc_list.append({k: p})

        print(str(kwargs['perc_size']) + 'th percentile fire sizes for the zones requested are:', perc_list)

        fires_dummy = []
        for fire in fires_clip:
            for zone in perc_list:
                if fire['UGC_ZONE'] in zone:
                    if fire['SIZE_AC'] >= zone[fire['UGC_ZONE']]:
                        fires_dummy.append(fire)

        fires_clip = fires_dummy

    fire_days = set([(str(fire['DISC_DATE'])[:8], fire['UGC_ZONE']) for fire in fires_clip])
    rfw_days = set([(rfw['FLAT_DATE'], rfw['NWS_UGC']) for rfw in rfws_clip])

    rfw_hits = set()
    fire_hits = set()
    for rfw_day in rfw_days:
        # for each rfw
        for fire_day in fire_days:
            # for every fire
            if rfw_day[1] == fire_day[1]:
                rfwday = datetime.strptime(rfw_day[0], '%Y%m%d')
                fireday = datetime.strptime(fire_day[0], '%Y%m%d')
                if (rfwday == fireday):
                    # or (rfwday + timedelta(days=1) == fireday) or \
                    #    (rfwday + timedelta(days=2) == fireday) or (rfwday + timedelta(days=-1) == fireday)
                    rfw_hits.add(rfw_day)
                    fire_hits.add(fire_day) # only allows unique records [(x,y),(z,a)] where x and z are dates and y and a are zones

                    # rfw = 20090606
                    # looking for fires
                    #     20090606, 20090607
                    #     hit, miss
                    #     # omit any non-rfw forecasts the day after a RFW issued



    # possible need to rewrite to preserve order of operations regarding day comparisons
    # =, then +1, then +2


    FIRE_DAYS = len(fire_days)
    RFW_DAYS = len(rfw_days)

    HITS = len(rfw_hits)
    MISSES = len(fire_days) - len(fire_hits)
    FALSE_ALARMS = len(rfw_days) - HITS

    BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
    POD = HITS / (HITS + MISSES)
    FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
    SR = HITS / (HITS + FALSE_ALARMS)
    TS = HITS / (HITS + MISSES + FALSE_ALARMS)

    FORECAST_DICT = {
        'FIRE_DAYS': FIRE_DAYS,
        'RFW_DAYS': RFW_DAYS,
        'HITS': HITS,
        'MISSES': MISSES,
        'FALSE_ALARMS': FALSE_ALARMS,
        'BIAS': BIAS,
        'POD': POD,
        'FAR': FAR,
        'SR': SR,
        'TS': TS
    }

    print("\nFIRE DAYS: %i, RFW DAYS: %i" % (FIRE_DAYS, RFW_DAYS))

    print("\nFORECAST - BASIC SKILL METRICS")
    print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
    print("BIAS: %f, POD: %f, FAR: %f, SR: %f, TS: %f" % (BIAS, POD, FAR, SR, TS))

    date_range = [i for i in range(-15, 16) if i != 0]  # Doesn't pick up 0
    year_range = [i for i in range(2006, 2016)]

    climo_rfws = set()
    for rfw in rfw_days:
        delta_days = random.choice(date_range)
        new_year = random.choice(year_range)

        rfwday = (datetime.strptime(rfw[0], '%Y%m%d') + timedelta(days=delta_days))
        if rfwday.strftime('%Y%m%d')[4:] == '0229':
            leap_years = [2008, 2012]
            new_year = random.choice(leap_years)
        rfwday = rfwday.replace(year=new_year).strftime('%Y%m%d')
        climo_rfws.add((rfwday, rfw[1]))

    rfw_hits = set()
    fire_hits = set()

    # elminate any days from being in contingency table that are non-rfw days that are adjacent to a rfw day

    # 20190815 rfw issued... tomorrow, next and next no RFW
    # forecast verification, economicssss lagged forecasts skill
        # ^^^^ #
    # this is a big deal if the decision changes the story. 

    for rfw_day in climo_rfws:
        for fire_day in fire_days:
            if rfw_day[1] == fire_day[1]:
                rfwday = datetime.strptime(rfw_day[0], '%Y%m%d')
                fireday = datetime.strptime(fire_day[0], '%Y%m%d')
                if (rfwday == fireday):
                    # or (rfwday + timedelta(days=1) == fireday) or \
                    #    (rfwday + timedelta(days=2) == fireday) or (rfwday + timedelta(days=-1) == fireday)
                    rfw_hits.add(rfw_day)
                    fire_hits.add(fire_day)

    FIRE_DAYS = len(fire_days)
    RFW_DAYS = len(rfw_days)

    MISSES = len(fire_days) - len(fire_hits)
    HITS = len(rfw_hits)
    FALSE_ALARMS = len(rfw_days) - HITS

    BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
    POD = HITS / (HITS + MISSES)
    FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
    SR = HITS / (HITS + FALSE_ALARMS)
    TS = HITS / (HITS + MISSES + FALSE_ALARMS)

    CLIMO_DICT = {
        'FIRE_DAYS': FIRE_DAYS,
        'RFW_DAYS': RFW_DAYS,
        'HITS': HITS,
        'MISSES': MISSES,
        'FALSE_ALARMS': FALSE_ALARMS,
        'BIAS': BIAS,
        'POD': POD,
        'FAR': FAR,
        'SR': SR,
        'TS': TS
    }

    print("\nRANDOM CLIMO - BASIC SKILL METRICS")
    print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
    print("BIAS: %f, POD: %f, FAR: %f, SR: %f, TS: %f" % (BIAS, POD, FAR, SR, TS))

    # GENERIC SKILL SCORE
    SKILL_DICT = {'BIAS_SS': (FORECAST_DICT['BIAS'] - CLIMO_DICT['BIAS']) / (1 - CLIMO_DICT['BIAS']),
                  'POD_SS': (FORECAST_DICT['POD'] - CLIMO_DICT['POD']) / (1 - CLIMO_DICT['POD']),
                  'FAR_SS': (FORECAST_DICT['FAR'] - CLIMO_DICT['FAR']) / (0 - CLIMO_DICT['FAR']),
                  'SR_SS': (FORECAST_DICT['SR'] - CLIMO_DICT['SR']) / (1 - CLIMO_DICT['SR']),
                  'TS_SS': (FORECAST_DICT['TS'] - CLIMO_DICT['TS']) / (1 - CLIMO_DICT['TS']),
                  'ETS': (FORECAST_DICT['HITS'] - CLIMO_DICT['HITS']) / (
                              FORECAST_DICT['HITS'] + FORECAST_DICT['MISSES'] + FORECAST_DICT['FALSE_ALARMS'] -
                              CLIMO_DICT['HITS'])
                  }
    print("\nSKILL SCORES AGAINST RANDOM CLIMATOLOGY")
    print("BIAS_SS: %f, POD_SS: %f, FAR_SS: %f, SR_SS: %f, TS_SS: %f, ETS: %f" % (
    SKILL_DICT['BIAS_SS'], SKILL_DICT['POD_SS'], SKILL_DICT['FAR_SS'], SKILL_DICT['SR_SS'], SKILL_DICT['TS_SS'],
    SKILL_DICT['ETS']))

    return FORECAST_DICT, CLIMO_DICT, SKILL_DICT

# POD by WFO, by month as a seaborn heatmap
# ERC percentile of fires that were hits hexbin

verify(20060101, 20151231, perc_size=90)

# , nfdrs_param=('BI_PERC', '>=', 90)
