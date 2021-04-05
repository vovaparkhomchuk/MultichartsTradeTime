from datetime import timedelta
import xlsxwriter
import datetime
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import collections

FORMAT_DATE = '%m/%d/%y %I:%M:%S %p'
# number = 41333.5

with open("NQ_Orders10Y_new.csv") as f:
    input_file = list(csv.DictReader(f, delimiter=";"))

"""
list_of_trades fields:
- date_in
- date_out
- price_in
- price_out
- profit
- type
"""
list_of_trades = []

for i in range(len(input_file)):
    if input_file[i]['Profit ($)']:
        date_out = datetime.datetime.strptime(str(input_file[i+1]['Date'])+' '+
                                    str(input_file[i+1]['Time']), FORMAT_DATE)
        date_in = datetime.datetime.strptime(str(input_file[i]['Date'])+' '+
                                     str(input_file[i]['Time']), FORMAT_DATE)
        trade = {
            "date_in": date_in,
            "date_out": date_out,
            "price_in": input_file[i]['Price'],
            "price_out": input_file[i+1]['Price'],
            "profit": input_file[i]['Profit ($)'],
            "type": "long" if input_file[i+1]['Type'] == "ExitLong" else "short"
        }
        list_of_trades.append(trade)

hours = list(range(0,24))
days = []
day_start = list_of_trades[0]['date_in'].date()
day_end = list_of_trades[len(list_of_trades)-1]['date_out'].date()
delta = day_end - day_start

for i in range(delta.days + 1):
    day = day_start + timedelta(days=i)
    normal_date = day.strftime('%m/%d/%Y')
    days.append(day)

res = {}

for i in days:
    res[i] = ["" for j in hours]

trade_hours = []
profits = []
types = []

for i, v in enumerate(list_of_trades):
    trade_start = v['date_in']
    trade_end = v['date_out']
    one_hour = datetime.timedelta(hours=1)

    one_trade = []

    while trade_start < trade_end:
        one_trade.append(trade_start)
        trade_start += one_hour

    trade_hours.append(one_trade)
    profits.append(list_of_trades[i]['profit'])
    types.append(list_of_trades[i]['type'])




for k, v in enumerate(trade_hours):
    for i, val in enumerate(v):
        if float(profits[k]) > 0:
            res[val.date()][val.hour] = "+prof {}".format(types[k][0])
        else:
            res[val.date()][val.hour] = "-prof {}".format(types[k][0])

result = []
result.append(['date',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])

for i, val in enumerate(res):
    day = []
    day.append(val)
    for hour in res[val]:
        day.append((hour))
    result.append(day)

for i, v in enumerate(result):
    if i > 0:
        result[i][0] = str(result[i][0])

for i, v in enumerate(result):
    if i > 0:
        day = datetime.datetime.strptime(v[0], '%Y-%m-%d')
        if day.weekday() == 4:
            for j in range(17, 25):
                v[j] = 'wknd'
        elif day.weekday() == 5:
            for j in range(1, 25):
                v[j] = 'wknd'
        elif day.weekday() == 6:
            for j in range(1, 18):
                v[j] = 'wknd'

list_of_profit_trades_at_time = {}
list_of_unprofit_trades_at_time = {}
list_of_profit_trades_at_time_out = {}
list_of_unprofit_trades_at_time_out = {}

list_of_profit_trades_at_time_with_prof = {}
list_of_unprofit_trades_at_time_with_prof = {}
list_of_profit_trades_at_time_out_with_prof = {}
list_of_unprofit_trades_at_time_out_with_prof = {}

list_of_profit_trades_at_time_with_hours = {}
list_of_unprofit_trades_at_time_with_hours = {}

for i in hours:
    list_of_profit_trades_at_time[i] = 0
    list_of_unprofit_trades_at_time[i] = 0
    list_of_profit_trades_at_time_out[i] = 0
    list_of_unprofit_trades_at_time_out[i] = 0

    list_of_profit_trades_at_time_with_prof[i] = 0
    list_of_unprofit_trades_at_time_with_prof[i] = 0
    list_of_profit_trades_at_time_out_with_prof[i] = 0
    list_of_unprofit_trades_at_time_out_with_prof[i] = 0

    list_of_profit_trades_at_time_with_hours[i] = 0
    list_of_unprofit_trades_at_time_with_hours[i] = 0

average_profit_per_trade_hour_prof = {}
average_profit_per_trade_hour_unprof = {}
# for i in hours:
#     average_profit_per_trade_hour_prof[i] = []
#     average_profit_per_trade_hour_unprof[i] = []

# print(len(list_of_trades))
for i in list_of_trades:
    # print(i)
    # if ((i['date_out'] - i['date_in']).days > 0 and (i['date_out'].weekday() < i['date_in'].weekday() or i['date_out'].weekday() == 6)):

    if ((i['date_out'].weekday() < i['date_in'].weekday() or i['date_out'].weekday() == 6)):
        continue

    # print(i['date_in'], i['date_in'].weekday(), i['date_out'], i['date_out'].weekday(),
    #       str(i['date_out'] - i['date_in']), (i['date_out'] - i['date_in']).days)

    if float(i['profit']) > 0:
        list_of_profit_trades_at_time[i['date_in'].hour] += 1
        list_of_profit_trades_at_time_out[i['date_out'].hour] += 1
        list_of_profit_trades_at_time_with_prof[i['date_in'].hour] += float(i['profit'])
        list_of_profit_trades_at_time_out_with_prof[i['date_out'].hour] += float(i['profit'])

        delta = i['date_out'] - i['date_in']
        days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
        total = (days*24*60 + hours * 60 + minutes) / 60
        list_of_profit_trades_at_time_with_hours[i['date_in'].hour] += total

        if total in average_profit_per_trade_hour_prof.keys():
            average_profit_per_trade_hour_prof[round(total)].append(float(i['profit']))
        else:
            average_profit_per_trade_hour_prof[round(total)] = [float(i['profit'])]

    else:
        list_of_unprofit_trades_at_time[i['date_in'].hour] += 1
        list_of_unprofit_trades_at_time_out[i['date_out'].hour] += 1
        list_of_unprofit_trades_at_time_with_prof[i['date_in'].hour] += float(i['profit'])
        list_of_unprofit_trades_at_time_out_with_prof[i['date_out'].hour] += float(i['profit'])

        delta = i['date_out'] - i['date_in']
        days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
        total = (days * 24 * 60 + hours * 60 + minutes) / 60
        list_of_unprofit_trades_at_time_with_hours[i['date_in'].hour] += total

        if total in average_profit_per_trade_hour_unprof.keys():
            average_profit_per_trade_hour_unprof[round(total)].append(float(i['profit']))
        else:
            # print([float(i['profit'])])
            average_profit_per_trade_hour_unprof[round(total)] = [float(i['profit'])]



# print(average_profit_per_trade_hour_prof)
# print(average_profit_per_trade_hour_unprof)

# average_profit_per_trade_hour_prof = dict(collections.OrderedDict(sorted(average_profit_per_trade_hour_prof.items())))
# average_profit_per_trade_hour_unprof = dict(collections.OrderedDict(sorted(average_profit_per_trade_hour_unprof.items())))

# hours_for_average_prof = list(average_profit_per_trade_hour_prof.keys())
# hours_for_average_unprof = list(average_profit_per_trade_hour_unprof.keys())

# men_means = [sum(average_profit_per_trade_hour_prof[i]) / len(average_profit_per_trade_hour_prof[i]) for i in average_profit_per_trade_hour_prof]
# women_means = [sum(average_profit_per_trade_hour_unprof[i]) / len(average_profit_per_trade_hour_unprof[i]) for i in average_profit_per_trade_hour_unprof]
# x = np.arange(len(hours_for_average_unprof))  # the label locations
# width = 0.35  # the width of the bars

# fig, ax = plt.subplots()
# print(x)
# rects1 = ax.bar(x - width/2, men_means, width, label='Average Profit')
# rects2 = ax.bar(x - width/2, women_means, width, label='Average Loss')

# Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Scores')
# ax.set_title('Average Loss (Trade Length)')
# ax.set_xticks(x)
# ax.set_xticklabels(hours_for_average_unprof)
# ax.legend()

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


# autolabel(rects1)
# autolabel(rects2)
#
# fig.tight_layout()
#
# plt.show()
#
# exit()

f = open("test1.txt", "w")
f.write(str(list_of_profit_trades_at_time))
f.close()

labels = list(range(0, 24))
# men_means = [list_of_profit_trades_at_time[i] for i in list_of_profit_trades_at_time]
# women_means = [list_of_unprofit_trades_at_time[i] for i in list_of_unprofit_trades_at_time]
# men_means = [list_of_profit_trades_at_time_out[i] for i in list_of_profit_trades_at_time_out]
# women_means = [list_of_unprofit_trades_at_time_out[i] for i in list_of_unprofit_trades_at_time_out]
# men_means = [list_of_profit_trades_at_time_with_prof[i] for i in list_of_profit_trades_at_time_with_prof]
# women_means = [list_of_unprofit_trades_at_time_with_prof[i] for i in list_of_unprofit_trades_at_time_with_prof]
# men_means = [list_of_profit_trades_at_time_out_with_prof[i] for i in list_of_profit_trades_at_time_out_with_prof]
# women_means = [list_of_unprofit_trades_at_time_out_with_prof[i] for i in list_of_unprofit_trades_at_time_out_with_prof]
men_means = [round(list_of_profit_trades_at_time_with_hours[i] / list_of_profit_trades_at_time[i] if list_of_profit_trades_at_time[i] != 0 else 1) for i in list_of_profit_trades_at_time_with_hours]
women_means = [round(list_of_unprofit_trades_at_time_with_hours[i] / list_of_unprofit_trades_at_time[i] if list_of_unprofit_trades_at_time[i] != 0 else 1) for i in list_of_unprofit_trades_at_time_with_hours]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars
# exit()

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, men_means, width, label='Profit')
rects2 = ax.bar(x + width/2, women_means, width, label='Loss')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Scores')
ax.set_title('List Of Profit Trades At Time With Hours')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

plt.show()

# exit()

workbook = xlsxwriter.Workbook('result.xlsx')
worksheet = workbook.add_worksheet()
prof_minus = workbook.add_format({'bg_color': '#FFC7CE'})
prof_plus = workbook.add_format({'bg_color': '#00ff80'})
weekend = workbook.add_format({'bg_color': '#34cceb'})
# print(result)
for row, row_data in enumerate(result):
    worksheet.write_row(row, 0, row_data)

worksheet.conditional_format('A1:Z{}'.format(len(result)), {'type':     'cell',
                                       'criteria': 'containing',
                                       'value':    '"-prof"',
                                       'format':   prof_minus})
worksheet.conditional_format('A1:Z{}'.format(len(result)), {'type':     'cell',
                                       'criteria': 'containing',
                                       'value':    '"+prof"',
                                       'format':   prof_plus})

worksheet.conditional_format('A1:Z{}'.format(len(result)), {'type':     'cell',
                                       'criteria': 'containing',
                                       'value':    '"wknd"',
                                       'format':   weekend})

workbook.close()
