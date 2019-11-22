import json
import datetime

with open('data/Dump/RedFlags_Northwest.json') as e:
    rfws = json.load(e)

    RFWS_flattened = []
    for rfw in rfws:
        iss_date = datetime.datetime.strptime(rfw['ISSUED'], '%Y%m%d%H%M')
        exp_date = datetime.datetime.strptime(rfw['EXPIRED'], '%Y%m%d%H%M')
        
        date_delta = ((exp_date-iss_date).seconds / 60) / 60
        start_hour = rfw['ISSUED'][8:10]
        starttime_delta = 24 - int(start_hour)

        # Stays within one day
        if starttime_delta >= date_delta:
            print(type(iss_date.strftime('%Y%m%d')))
            flat_date = iss_date.strftime('%Y%m%d')
            record = {
                      "OBJECTID": 0,
                      "WFO": rfw['WFO'],
                      "ISSUED": rfw['ISSUED'] ,
                      "EXPIRED": rfw['EXPIRED'],
                      "INIT_ISS": rfw['INIT_ISS'],
                      "INIT_EXP": rfw['INIT_EXP'],
                      "STATUS": rfw['STATUS'],
                      "NWS_UGC": rfw['NWS_UGC'],
                      "STATE": rfw['STATE'],
                      "FLAT_DATE": flat_date,
                      "RFW_DAYS": "1 day",
            }

            RFWS_flattened.append(record)

        # Two days
        else:
            iss_date = datetime.datetime.strptime(rfw['ISSUED'][:8], '%Y%m%d')
            exp_date = datetime.datetime.strptime(rfw['EXPIRED'][:8], '%Y%m%d')
            print(iss_date, exp_date)
            while iss_date <= exp_date:
                flat_date = iss_date.strftime('%Y%m%d')
                iss_date += datetime.timedelta(days=1)

                record = {
                    "OBJECTID": 0,
                    "WFO": rfw['WFO'],
                    "ISSUED": rfw['ISSUED'],
                    "EXPIRED": rfw['EXPIRED'],
                    "INIT_ISS": rfw['INIT_ISS'],
                    "INIT_EXP": rfw['INIT_EXP'],
                    "STATUS": rfw['STATUS'],
                    "NWS_UGC": rfw['NWS_UGC'],
                    "STATE": rfw['STATE'],
                    "FLAT_DATE": flat_date,
                    "RFW_DAYS": "2 days",
                }

                RFWS_flattened.append(record)

id = 0
for rfw in RFWS_flattened:
    # rfw['LEAD_TIME'] = (datetime.datetime.strptime(rfw['ISSUED'], '%Y%m%d%H%M') - datetime.datetime.strptime(rfw['INIT_ISS'], '%Y%m%d%H%M')).seconds / 3600.0
    rfw['OBJECTID'] = id
    id += 1

with open('RFWs_Northwest.json', 'w') as outfile:
    json.dump(RFWS_flattened, outfile, indent=4, sort_keys=True, default=str)


