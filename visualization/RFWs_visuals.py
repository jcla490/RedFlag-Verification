from collections import Counter
import datetime
import json
import matplotlib.pyplot as plt

# Global JSON data files
with open('data/RFWs_Northwest.json') as e:
    rfws = json.load(e)


########################################################################################################################
# YEAR FREQUENCY OF RFWS                                                                                               #
########################################################################################################################
def rfws_by_year(rfws):
    years = []
    for rfw in rfws:
        years.append(rfw['ISSUED'][:4])
    year_count = Counter(years)
    print(year_count)
    plt.scatter(year_count.keys(), year_count.values(), edgecolor='black', linewidth=1.0)
    plt.title("Frequency of RFWs by Year")
    plt.ylabel("Number of Forecasts")
    plt.xlabel("Year")
    plt.savefig('graphics/rfws_by_year.png', dpi=600)
    plt.show()

rfws_by_year(rfws)

########################################################################################################################
# MONTH FREQUENCY OF RFWS                                                                                              #
########################################################################################################################
def rfws_by_month(rfws):
    months = []
    for rfw in rfws:
        months.append(rfw['ISSUED'][4:6])
    month_count = Counter(months)
    print(month_count)
    plt.bar(month_count.keys(), month_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of RFWs by Month")
    plt.ylabel("Number of Forecasts")
    plt.xlabel("Month")
    plt.savefig('graphics/rfws_by_month.png', dpi=600)
    plt.show()

rfws_by_month(rfws)

########################################################################################################################
# RFW FREQUENCY BY WFO                                                                                                 #
########################################################################################################################
def rfws_by_wfo(rfws):
    office = []
    for rfw in rfws:
        office.append(rfw['WFO'])
    office_count = Counter(office)
    print(office_count)
    plt.bar(office_count.keys(), office_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of Red Flag Warnings Issued by Office")
    plt.ylabel("Number of Forecasts")
    plt.xlabel("Office")
    plt.savefig('graphics/rfws_by_wfo.png', dpi=600)
    plt.show()

rfws_by_wfo(rfws)

########################################################################################################################
# RFW FREQUENCY BY ZONE                                                                                                #
########################################################################################################################
def rfws_by_zone(rfws):
    zones = []
    for rfw in rfws:
        zones.append(rfw['NWS_UGC'])
    zone_count = Counter(zones)
    print(zone_count)
    plt.bar(zone_count.keys(), zone_count.values(), edgecolor='black', linewidth=1.0, width=1)
    plt.title("Frequency of Red Flag Warnings Issued by Zone")
    plt.ylabel("Number of Forecasts")
    plt.xlabel("Zone")
    plt.savefig('graphics/rfws_by_zone.png', dpi=600)
    plt.show()

rfws_by_zone(rfws)

########################################################################################################################
# RFW LENGTH                                                                                                           #
########################################################################################################################
def rfws_length(rfws):
    date_diffs = []
    for rfw in rfws:
        start = rfw['ISSUED']
        end = rfw['EXPIRED']
        start_datetime = datetime.datetime.strptime(start, "%Y%m%d%H%M")
        end_datetime = datetime.datetime.strptime(end, "%Y%m%d%H%M")
        hours = (end_datetime - start_datetime).seconds / 3600
        date_diffs.append(hours)
    plt.hist(date_diffs, bins=[0, 3, 6, 12, 18, 24], edgecolor='black', linewidth=1.0)
    plt.title('Red Flag Warning Duration (Hours)')
    plt.ylabel('Frequency')
    plt.xlabel('Duration of Red Flag Event (Hours)')
    plt.xticks([0, 3, 6, 12, 18, 24])
    plt.savefig('graphics/rfws_by_duration.png', dpi=600)
    plt.show()

rfws_length(rfws)