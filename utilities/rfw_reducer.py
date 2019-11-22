import json
import datetime

with open('data/2006_2015_lower48_allRFWs_allActions.json') as e:
    rfws = json.load(e)
    rfws_reduced = []
    counter = 0
    for rfw in rfws['features']:
        if rfw['attributes']["WFO"] in ['MSO', "PIH", "BOI", "SEW", "MFR", "PQR", "PDT", "OTX"]:
            if rfw['attributes']["PHENOM"] == 'FW':
                if rfw['attributes']["SIG"] == 'W':
                    record = {
                        "WFO": rfw['attributes']["WFO"],
                        "ISSUED": rfw['attributes']["ISSUED"],
                        "EXPIRED": rfw['attributes']["EXPIRED"],
                        "INIT_ISS": rfw['attributes']["INIT_ISS"],
                        "INIT_EXP": rfw['attributes']["INIT_EXP"],
                        "STATUS": rfw['attributes']["STATUS"],
                        "NWS_UGC": rfw['attributes']["NWS_UGC"],
                        "STATE": rfw['attributes']["calc_state"],
                    }
                    rfws_reduced.append(record)
                    counter += 1
                    print(str(counter) + " fires counted!")

with open('data/RedFlags_Northwest.json', 'w') as outfile:
    json.dump(rfws_reduced, outfile, indent=4, sort_keys=True, default=str)
    print("done writing")