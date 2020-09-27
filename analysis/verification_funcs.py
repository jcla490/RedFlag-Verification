from datetime import datetime, timedelta
import numpy as np
import random
import json
import statistics as stat


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

        Returns: None, although it prepares self.rfws and self.fires for other methods.
        """

        start_rfw_len = len(self.rfws)
        start_fires_len = len(self.fires)

        # Reduce datasets to WFOs specified
        if 'wfo' in kwargs:
            if type(kwargs['wfo']) is list:
                self.rfws = [rfw for rfw in self.rfws if rfw['WFO'] in kwargs['wfo']]
                self.fires = [fire for fire in self.fires if fire['WFO'] in kwargs['wfo']]
            else: 
                self.rfws = [rfw for rfw in self.rfws if rfw['WFO'] == kwargs['wfo']]
                self.fires = [fire for fire in self.fires if fire['WFO'] == kwargs['wfo']]

        # First get percentile sizes so we don't calculate based off a smol dataset
        if 'perc_size' in kwargs:
            zone_sizes = {}
            for fire in self.fires:
                if fire['UGC_ZONE'] in zone_sizes:
                    zone_sizes[fire['UGC_ZONE']].append(fire['SIZE_AC'])
                else:
                    zone_sizes[fire['UGC_ZONE']] = [fire['SIZE_AC']]

            perc_list = []
            med_list = []
            for k, v in zone_sizes.items():
                m = np.array(v)
                p = np.percentile(m, kwargs['perc_size'])
                perc_list.append({k: p})

            print(str(kwargs['perc_size']) + 'th percentile fire sizes for the zones requested are:', perc_list)
            size_list = []
            for zone in perc_list:
                size_list.append(list(zone.values())[0])
            print(size_list)
            # print(sum(size_list)/len(size_list))


            fires_dummy = []
            size_dummy = []
            for fire in self.fires:
                for zone in perc_list:
                    if fire['UGC_ZONE'] in zone:
                        if fire['SIZE_AC'] >= zone[fire['UGC_ZONE']]:
                            fires_dummy.append(fire)
                            size_dummy.append(fire['SIZE_AC'])
            print(np.mean(size_dummy))

            self.fires = fires_dummy

        # Reduce dataset sizes bigly by limiting to user start/end dates
        self.rfws = [rfw for rfw in self.rfws if datetime.strptime(str(start_date), '%Y%m%d') <=
                    datetime.strptime(rfw['FLAT_DATE'], '%Y%m%d') <= datetime.strptime(str(end_date), '%Y%m%d')]
        self.fires = [fire for fire in self.fires if datetime.strptime(str(start_date), '%Y%m%d') <=
                    datetime.strptime(str(fire['DISC_DATE'])[:8], '%Y%m%d') <= datetime.strptime(str(end_date), '%Y%m%d') + timedelta(days=1)]
        
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
            self.fires = [fire for fire in self.fires if fire['FORESTED'] == kwargs['forestcover']]

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
            if fd_operator == '<':
                self.fires = [fire for fire in self.fires if fire[fd_index] < fd_threshold]
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
        print("Number of fires before reduced to days only is {}".format(len(self.fires)))
        # Unique fire days and rfw days only!
        self.fire_days = set([(str(fire['DISC_DATE'])[:8], fire['UGC_ZONE']) for fire in self.fires])
        self.rfw_days = set([(rfw['FLAT_DATE'], rfw['NWS_UGC']) for rfw in self.rfws])
        fin_rfw_len = len(self.rfw_days)
        fin_fires_len = len(self.fire_days)

        print('\nELIMINATE MULTIPLE FIRES/RFWS FOR SAME DAY/ZONE:')
        print('RFWs reduced from %i to %i' % (start_rfw_len, fin_rfw_len))
        print('Fires reduced from %i to %i' % (start_fires_len, fin_fires_len))

        return

    def forecast_skill_scores(self):

        exact_matches = self.rfw_days.intersection(self.fire_days)
        # increment RFW by 1 day
        day_2_rfws = set()
        for rfw in self.rfw_days:
            day_2_rfws.add(((datetime.strptime(rfw[0], '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d'), rfw[1])) 
        
        day_2_matches = day_2_rfws.intersection(self.fire_days)

        day2matches_corr = set()
        for d2match in day_2_matches:
            day2matches_corr.add(((datetime.strptime(d2match[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d'), d2match[1]))

        rfw_matches = exact_matches | day2matches_corr
        fire_matches = exact_matches | day_2_matches

        for match in rfw_matches:
            self.rfw_days.remove(match)

        for match in fire_matches:
            self.fire_days.remove(match)

        # print("\n\nFirst day matches: " + str(len(rfw_matches)))
        # print("New set sizes: RFW_DAYS = " + str(len(self.rfw_days)) + ", FIRE_DAYS = " + str(len(self.fire_days)))

        HITS = len(rfw_matches)  # this is hits for first day and second
        MISSES = len(self.fire_days) # and exact misses
        FALSE_ALARMS = len(self.rfw_days) # and exact false alarms

        print("\nFORECAST - BASIC SKILL METRICS")
        print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
        BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
        POD = HITS / (HITS + MISSES)
        FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
        CSI = HITS / (HITS + MISSES + FALSE_ALARMS)


        self.FORECAST_DICT = {
            'HITS': HITS,
            'MISSES': MISSES,
            'FALSE_ALARMS': FALSE_ALARMS,
            'BIAS': BIAS,
            'POD': POD,
            'FAR': FAR,
            'CSI': CSI
        }
        
        print("POD: %f, FAR: %f, CSI: %f" % (POD, FAR, CSI))

        return self.FORECAST_DICT

    def climo_skill_scores(self, forecast_dict):
        climo_score_list = []
        for i in range(100):
            # Recreate rfw_days and fire_days since we messed with em previously
            # Unique fire days and rfw days only!
            fire_days = set([(str(fire['DISC_DATE'])[:8], fire['UGC_ZONE']) for fire in self.fires])
            rfw_days = set([(rfw['FLAT_DATE'], rfw['NWS_UGC']) for rfw in self.rfws])

            # print('CLIMO_METHOD')
            # print(len(fire_days), len(rfw_days))
            
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
            exact_matches = climo_rfws.intersection(fire_days)

            # increment RFW by 1 day
            day_2_rfws = set()
            for rfw in climo_rfws:
                day_2_rfws.add(((datetime.strptime(rfw[0], '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d'), rfw[1])) 
            
            day_2_matches = day_2_rfws.intersection(fire_days)

            day2matches_corr = set()
            for d2match in day_2_matches:
                day2matches_corr.add(((datetime.strptime(d2match[0], '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d'), d2match[1]))

            rfw_matches = exact_matches | day2matches_corr
            fire_matches = exact_matches | day_2_matches
            for match in rfw_matches:
                climo_rfws.remove(match)

            for match in fire_matches:
                fire_days.remove(match)


            HITS = len(rfw_matches) # this is hits for first day and second
            MISSES = len(fire_days) # and exact misses
            FALSE_ALARMS = len(climo_rfws) # and exact false alarms

            BIAS = (HITS + FALSE_ALARMS) / (HITS + MISSES)
            POD = HITS / (HITS + MISSES)
            FAR = FALSE_ALARMS / (HITS + FALSE_ALARMS)
            CSI = HITS / (HITS + MISSES + FALSE_ALARMS)

            CLIMO_DICT = {
                'HITS': HITS,
                'MISSES': MISSES,
                'FALSE_ALARMS': FALSE_ALARMS,
                'BIAS': BIAS,
                'POD': POD,
                'FAR': FAR,
                'CSI': CSI
            }
            # print(CLIMO_DICT)
            climo_score_list.append(CLIMO_DICT)
            # print("\nCLIMO - BASIC SKILL METRICS")
            # print("HITS: %i, MISSES: %i, FALSE ALARMS: %i" % (HITS, MISSES, FALSE_ALARMS))
            # print("BIAS: %f, POD: %f, FAR: %f, CSI: %f" % (BIAS, POD, FAR, CSI))

        bias_list, csi_list, pod_list, far_list, sig_list = [], [], [], [], []
        for result in climo_score_list:
            bias_list.append(result['BIAS'])
            pod_list.append(result['POD'])
            far_list.append(result['FAR'])
            csi_list.append(result['CSI'])

            sig_list.append((forecast_dict['POD'] - result['POD'])  / (1 - result['POD']))
        bias_med = stat.median(sorted(bias_list))
        pod_med = stat.median(sorted(pod_list))
        far_med = stat.median(sorted(far_list))
        csi_med = stat.median(sorted(csi_list))
        sig_count = len([score for score in sig_list if score > 0])

        median_dict = {
                'BIAS': bias_med,
                'POD': pod_med,
                'FAR': far_med,
                'CSI': csi_med,
                'SIG_TEST': sig_count
        }

        print("\nCLIMO - BASIC SKILL METRICS")
        print("POD: %f, FAR: %f, CSI: %f, SIG_NUM: %i" % (pod_med, far_med, csi_med, sig_count))
        return median_dict


    def gen_skill_scores(self):

        self.FORECAST_DICT = self.forecast_skill_scores()
        self.CLIMO_DICT = self.climo_skill_scores(self.FORECAST_DICT)

        self.SKILL_DICT = {
            'BIAS_SS': (self.FORECAST_DICT['BIAS'] - self.CLIMO_DICT['BIAS']) / (1 - self.CLIMO_DICT['BIAS']),
            'POD_SS': (self.FORECAST_DICT['POD'] - self.CLIMO_DICT['POD']) / (1 - self.CLIMO_DICT['POD']),
            'FAR_SS': (self.FORECAST_DICT['FAR'] - self.CLIMO_DICT['FAR']) / (0 - self.CLIMO_DICT['FAR']),
            'CSI_SS': (self.FORECAST_DICT['CSI'] - self.CLIMO_DICT['CSI']) / (1 - self.CLIMO_DICT['CSI']),
        }

        print("\nSKILL SCORES AGAINST RANDOM CLIMATOLOGY")
        print("POD_SS: %f, FAR_SS: %f, CSI_SS: %f" % (self.SKILL_DICT['POD_SS'], self.SKILL_DICT['FAR_SS'], self.SKILL_DICT['CSI_SS']))

        return
