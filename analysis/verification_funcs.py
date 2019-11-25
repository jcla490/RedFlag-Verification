from datetime import datetime, timedelta
import numpy as np
import random
import json


class VerifySkill:

    def __init__(self, rfw_file_path, fires_file_path):
        self.rfw_file_path = rfw_file_path
        self.fires_file_path = fires_file_path

        with open(rfw_file_path) as e:
            self.rfws = json.load(e)

        with open(fires_file_path) as f:
            self.fires = json.load(f)

    def query_params(self, start_date, end_date, **kwargs):
        """
        Reduces size of RFWS json and Fires json based on user arguments

        Parameters:
            Positional:
            start_date (int) (required): A date in format YYYYMMDD signifying the beginning of the search period. Records occurring before this date will be omitted.
            end_date (int) (required): A date in format YYYYMMDD signifying the end of the search period. Records occurring after this date will be omitted.
            
            Keyword:
            wfo (str or list of strs) (optional): The weather forecast office(s) you would like to calculate skill for. Omit for all northwest WFOs.
            zone (str or list of strs) (optional): The fire weather zone(s) you would like to calculate skill for. Omit for all northwest FWZs.
            forest_cover (str) (optional): Set to 'yes' to only include forested fires. Set to 'no' for non-forested fires. Omit to show both types in results.
            cause (str) (optional): Specify "human" to find human-caused fires. Specify "lightning" for lightning-caused fires. Omit to both causes in results. 
            nfdrs_param (list of strs) (optional): Specify an NFDRS parameter (BI_PERC, FM100_PERC, ERC_PERC, FM1000_PER), an operation (<=, ==, >=) and some threshold
                                                   value to see fires that have matching fire danger parameters.
            duration (int): Specify either 6, 12, 18, or 24 to see only matching RFWs with event durations between these ranges. 
            perc_size (int): The percentile value for which returned fires should be above. 

        Returns: None, although it prepares self.rfws and self.fires for skill_calculator()
        """

        start_rfw_len = len(self.rfws)
        start_fires_len = len(self.fires)

        # First get percentile sizes so we don't calculate based off a smol dataset
        if 'perc_size' in kwargs:
            zone_sizes = {}
            for fire in self.fires:
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
            for fire in self.fires:
                for zone in perc_list:
                    if fire['UGC_ZONE'] in zone:
                        if fire['SIZE_AC'] >= zone[fire['UGC_ZONE']]:
                            fires_dummy.append(fire)

            self.fires = fires_dummy

        # Reduce dataset sizes bigly by limiting to user start/end dates
        self.rfws = [rfw for rfw in self.rfws if datetime.strptime(str(start_date), '%Y%m%d') <=
                    datetime.strptime(rfw['FLAT_DATE'], '%Y%m%d') <= datetime.strptime(str(end_date), '%Y%m%d')]
        self.fires = [fire for fire in self.fires if datetime.strptime(str(start_date), '%Y%m%d') <=
                    datetime.strptime(str(fire['DISC_DATE'])[:8], '%Y%m%d') <= datetime.strptime(str(end_date), '%Y%m%d')]

        # Reduce datasets to WFOs specified
        if 'wfo' in kwargs:
            if type(kwargs['wfo']) is list:
                self.rfws = [rfw for rfw in self.rfws if rfw['WFO'] in kwargs['wfo']]
                self.fires = [fire for fire in self.fires if fire['WFO'] in kwargs['wfo']]
            else: 
                self.rfws = [rfw for rfw in self.rfws if rfw['WFO'] == kwargs['wfo']]
                self.fires = [fire for fire in self.fires if fire['WFO'] == kwargs['wfo']]
        print(len(self.fires))
        print(len(self.rfws))

        # Reduce datasets to FWZs specified
        if 'zone' in kwargs:
            if type(kwargs['zone']) is list:
                self.rfws = [rfw for rfw in self.rfws if rfw['NWS_UGC'] in kwargs['zone']]
                self.fires = [fire for fire in self.fires if fire['UGC_ZONE'] in kwargs['zone']]
            else: 
                self.rfws = [rfw for rfw in self.rfws if rfw['NWS_UGC'] == kwargs['zone']]
                self.fires = [fire for fire in self.fires if fire['UGC_ZONE'] == kwargs['zone']]

        # Reduce fires dataset to forest type specified
        if 'forestcover' in kwargs:
            self.fires = [fire for fire in self.fires if fire['FORESTED'] == kwargs['forest_cover']]

        # Reduce fires dataset to ignition cause type specified
        if 'cause' in kwargs:
            if kwargs['cause'] == 'lightning':
                ltng_codes = ['1']
                self.fires = [fire for fire in self.fires if str(fire['STAT_CAUSE']) in ltng_codes]

            if kwargs['cause'] == 'human':
                human_codes = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
                self.fires = [fire for fire in self.fires if str(fire['STAT_CAUSE']) in human_codes]

        if 'nfdrs_param' in kwargs:
            fd_index, fd_operator, fd_threshold = kwargs['nfdrs_param'][0], kwargs['nfdrs_param'][1], kwargs['nfdrs_param'][2]
            if fd_operator == '<=':
                self.fires = [fire for fire in self.fires if fire[fd_index] <= fd_threshold]
            elif fd_operator == '==':
                self.fires = [fire for fire in self.fires if fire[fd_index] == fd_threshold]
            elif fd_operator == '>=':
                self.fires = [fire for fire in self.fires if fire[fd_index] >= fd_threshold]

        if 'duration' in kwargs:
            rfws_dummy = []
            for rfw in self.rfws:
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
            self.rfws = rfws_dummy

        # Unique fire days and rfw days only!
        self.fire_days = set([(str(fire['DISC_DATE'])[:8], fire['UGC_ZONE']) for fire in self.fires])
        self.rfw_days = set([(rfw['FLAT_DATE'], rfw['NWS_UGC']) for rfw in self.rfws])

        fin_rfw_len = len(self.rfw_days)
        fin_fires_len = len(self.fire_days)

        print('Query_params() complete. Results:')
        print('RFWs reduced from %i to %i' % (start_rfw_len, fin_rfw_len))
        print('Fires reduced from %i to %i' % (start_fires_len, fin_fires_len))

        return

    def forecast_skill_scores(self):

        # Get exact hits
        exact_matches = self.rfw_days.intersection(self.fire_days)
        print("First day matches: " + str(len(exact_matches)))

        # Remove them from main records
        for match in exact_matches:
            if match in self.fire_days:
                self.fire_days.remove(match)
            if match in self.rfw_days:
                self.rfw_days.remove(match)

        print("After first day sizes: FIRE_DAYS = " + str(len(self.fire_days)) + ", RFW_DAYS = " + str(len(self.rfw_days)) )

        # Get hits on fires that occurred one day after
        day_2_fires = set()
        for fire in self.fire_days:
            day_2_fires.add(((datetime.strptime(fire[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d'), fire[1]))
        secondary_matches = self.rfw_days.intersection(day_2_fires)
        
        print("Second day matches: " + str(len(secondary_matches)))

        # Remove these from main records
        for fire in self.fire_days.copy():
            if (((datetime.strptime(fire[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')), fire[1]) in secondary_matches:
                self.fire_days.remove(fire)
        for match in secondary_matches:
            if match in self.rfw_days:
                self.rfw_days.remove(match)

        print("After second day sizes: FIRE_DAYS = " + str(len(self.fire_days)) + ", RFW_DAYS = " + str(len(self.rfw_days)))

        HITS = len(exact_matches) + len(secondary_matches)  # this is hits for first day and second
        MISSES = len(self.fire_days) # and exact misses
        FALSE_ALARMS = len(self.rfw_days) # and exact false alarms

        BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
        POD = HITS / (HITS + MISSES)
        FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
        SR = HITS / (HITS + FALSE_ALARMS)
        TS = HITS / (HITS + MISSES + FALSE_ALARMS)

        self.FORECAST_DICT = {
            'HITS': HITS,
            'MISSES': MISSES,
            'FALSE_ALARMS': FALSE_ALARMS,
            'BIAS': BIAS,
            'POD': POD,
            'FAR': FAR,
            'SR': SR,
            'TS': TS
        }

        print("\nFORECAST - BASIC SKILL METRICS")
        print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
        print("BIAS: %f, POD: %f, FAR: %f, SR: %f, TS: %f" % (BIAS, POD, FAR, SR, TS))

        return self.FORECAST_DICT

    def climo_skill_scores(self):

        # Recreate rfw_days and fire_days since we messed with em previously
        # Unique fire days and rfw days only!
        fire_days = set([(str(fire['DISC_DATE'])[:8], fire['UGC_ZONE']) for fire in self.fires])
        rfw_days = set([(rfw['FLAT_DATE'], rfw['NWS_UGC']) for rfw in self.rfws])
        
        day_range = [i for i in range(-15, 16) if i != 0]  # Doesn't pick up 0
        year_range = [i for i in range(2006, 2016)]

        climo_rfws = set()
        for rfw in rfw_days: 
            delta_days = random.choice(day_range)
            random_year = random.choice(year_range)
            rfwday = (datetime.strptime(rfw[0], '%Y%m%d') + timedelta(days=delta_days))
            if rfwday.strftime('%Y%m%d')[4:] == '0229':
                leap_years = [2008, 2012]
                random_year = random.choice(leap_years)
            rfwday = rfwday.replace(year=random_year).strftime('%Y%m%d')
            climo_rfws.add((rfwday, rfw[1]))
        print(len(climo_rfws))

        # Get exact hits
        exact_matches = climo_rfws.intersection(fire_days)
        print("First day CLIMO matches: " + str(len(exact_matches)))

        # Remove them from main records
        for match in exact_matches:
            if match in fire_days:
                fire_days.remove(match)
            if match in climo_rfws:
                climo_rfws.remove(match)

        print("After first day CLIMO sizes: FIRE_DAYS = " + str(len(fire_days)) + ", RFW_DAYS = " + str(len(climo_rfws)) )

        # Get hits on fires that occurred one day after
        day_2_fires = set()
        for fire in fire_days:
            day_2_fires.add(((datetime.strptime(fire[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d'), fire[1]))
        secondary_matches = climo_rfws.intersection(day_2_fires)
        
        print("Second day matches: " + str(len(secondary_matches)))

        # Remove these from main records
        for fire in fire_days.copy():
            if (((datetime.strptime(fire[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')), fire[1]) in secondary_matches:
                fire_days.remove(fire)
        for match in secondary_matches:
            if match in climo_rfws:
                climo_rfws.remove(match)

        print("After second day CLIMO sizes: FIRE_DAYS = " + str(len(fire_days)) + ", RFW_DAYS = " + str(len(climo_rfws)))

        HITS = len(exact_matches) + len(secondary_matches)  # this is hits for first day and second
        MISSES = len(fire_days) # and exact misses
        FALSE_ALARMS = len(climo_rfws) # and exact false alarms

        BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
        POD = HITS / (HITS + MISSES)
        FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
        SR = HITS / (HITS + FALSE_ALARMS)
        TS = HITS / (HITS + MISSES + FALSE_ALARMS)

        self.CLIMO_DICT = {
            'HITS': HITS,
            'MISSES': MISSES,
            'FALSE_ALARMS': FALSE_ALARMS,
            'BIAS': BIAS,
            'POD': POD,
            'FAR': FAR,
            'SR': SR,
            'TS': TS
        }

        print("\nCLIMO - BASIC SKILL METRICS")
        print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
        print("BIAS: %f, POD: %f, FAR: %f, SR: %f, TS: %f" % (BIAS, POD, FAR, SR, TS))

        return self.CLIMO_DICT


    def gen_skill_scores(self):

        FORECAST_DICT = self.forecast_skill_scores()
        CLIMO_DICT = self.climo_skill_scores()

        SKILL_DICT = {
            'BIAS_SS': (FORECAST_DICT['BIAS'] - CLIMO_DICT['BIAS']) / (1 - CLIMO_DICT['BIAS']),
            'POD_SS': (FORECAST_DICT['POD'] - CLIMO_DICT['POD']) / (1 - CLIMO_DICT['POD']),
            'FAR_SS': (FORECAST_DICT['FAR'] - CLIMO_DICT['FAR']) / (0 - CLIMO_DICT['FAR']),
            'SR_SS': (FORECAST_DICT['SR'] - CLIMO_DICT['SR']) / (1 - CLIMO_DICT['SR']),
            'TS_SS': (FORECAST_DICT['TS'] - CLIMO_DICT['TS']) / (1 - CLIMO_DICT['TS']),
            'ETS': (FORECAST_DICT['HITS'] - CLIMO_DICT['HITS']) / (FORECAST_DICT['HITS'] + FORECAST_DICT['MISSES'] + FORECAST_DICT['FALSE_ALARMS'] - CLIMO_DICT['HITS'])
        }

        print("\nSKILL SCORES AGAINST RANDOM CLIMATOLOGY")
        print("BIAS_SS: %f, POD_SS: %f, FAR_SS: %f, SR_SS: %f, TS_SS: %f, ETS: %f" % (SKILL_DICT['BIAS_SS'], SKILL_DICT['POD_SS'], SKILL_DICT['FAR_SS'], SKILL_DICT['SR_SS'], 
        SKILL_DICT['TS_SS'], SKILL_DICT['ETS']))

        return
