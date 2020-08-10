from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xlsxwriter
import datetime
import csv

FORMAT_DATE = '%Y/%m/%d %H:%M:%S'
number = 41333.5

input_file = list(csv.DictReader(open("Trade.csv")))

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
    if input_file[i]['Profit']:
        date_in = datetime.datetime.strptime(str(input_file[i-1]['Year'])+'/'+
                                    str(input_file[i-1]['Month'])+'/'+
                                    str(input_file[i-1]['Day'])+ ' '+
                                    str(input_file[i-1]['Hour'])+ ':'+
                                    str(input_file[i-1]['Minute']) + ':' +
                                    str(input_file[i-1]['Second'])
                                    ,
                                    FORMAT_DATE)
        date_out = datetime.datetime.strptime(str(input_file[i]['Year'])+'/'+
                                     str(input_file[i]['Month'])+'/'+
                                     str(input_file[i]['Day'])+ ' '+
                                     str(input_file[i]['Hour'])+ ':'+
                                     str(input_file[i]['Minute']) + ':' +
                                     str(input_file[i]['Second']),
                                     FORMAT_DATE)
        trade = {
            "date_in": date_in,
            "date_out": date_out,
            "price_in": input_file[i-1]['Price'],
            "price_out": input_file[i]['Price'],
            "profit": input_file[i]['Profit'],
            "type": "long" if input_file[i]['Type'] == "LExit" else "short"
        }
        list_of_trades.append(trade)

# print(list_of_trades)

hours = list(range(0,24))
days = []
day_start = list_of_trades[0]['date_in'].date()
day_end = list_of_trades[len(list_of_trades)-1]['date_out'].date()

delta = day_end - day_start

for i in range(delta.days + 1):
    day = day_start + timedelta(days=i)
    # day - day.strftime('%m/%d/%Y')
    # print(type(day))
    normal_date = day.strftime('%m/%d/%Y')
    # print(normal_date)
    days.append(day)


res = {}

for i in days:
    # res[i] = [{j:0} for j in hours]
    res[i] = ["" for j in hours]

trade_hours = []
profits = []

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
    # print(list_of_trades)




for k, v in enumerate(trade_hours):
    for i, val in enumerate(v):
        # print(val.date(), val.hour)
        # print(res[val.date()])
        if i == 0:
            # print("start: ", val)
            # res[val.date()][val.hour] = val.strftime("%d/%m/%Y, %H:%M:%S")
            res[val.date()][val.hour] = val.strftime("%H:%M:%S")
            # print("start: "+val.strftime("%d/%m/%Y, %H:%M:%S"))
        elif i == len(v)-1:
            # print("end: ", val)
            # res[val.date()][val.hour] = val.strftime("%d/%m/%Y, %H:%M:%S")
            res[val.date()][val.hour] = val.strftime("%H:%M:%S")
            # print("end: "+val.strftime("%d/%m/%Y, %H:%M:%S"))
        else:
            # print(v)
            if float(profits[k]) > 0:
                res[val.date()][val.hour] = "+1"
            else:
                res[val.date()][val.hour] = "-1"
    # print('-----')

# print(res)

result = []
result.append(['date',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23])

for i, val in enumerate(res):
    # print(val, res[val])
    day = []
    day.append(val)
    for hour in res[val]:
        day.append((hour))
    # print(day)
    result.append(day)


# with open("temp.csv", "w", newline="") as f:
#    writer = csv.writer(f)
#    writer.writerows(result)

# print(result)


# with xlsxwriter.Workbook('kek.xlsx', {'default_date_format':
#                                                   'dd/mm/yy hh:mm'}) as workbook:
#     # workbook.add_format({'num_format': 'dd/mm/yy hh:mm', 'bold': True, 'font_color': 'red'}, )
#     worksheet = workbook.add_worksheet()
#
#
#     for row_num, data in enumerate(result):
#         worksheet.write_row(row_num, 0, data)
#
#     efg = workbook.add_format({'bg_color': 'green'})
#     workbook.conditional_format(options={'value': 1, 'format': efg})


# print(result)

for i, v in enumerate(result):
    # for j, val in enumerate(v):
    if i > 0:
        result[i][0] = str(result[i][0])
        print(type(result[i][0]))
        # v[k] = 'jopa'
            # print(type(val))


workbook = xlsxwriter.Workbook('conditional_format.xlsx')
worksheet = workbook.add_worksheet()

# Add a format.
my_format = workbook.add_format({'bg_color': '#FFC7CE'})

my_format2 = workbook.add_format({'bg_color': '#00ff80	'})


for row, row_data in enumerate(result):
    worksheet.write_row(row, 0, row_data)

# Add a conditional format.
worksheet.conditional_format('A1:Z8', {'type':     'cell',
                                       'criteria': '==',
                                       'value':    '"-1"',
                                       'format':   my_format})
worksheet.conditional_format('A1:Z8', {'type':     'cell',
                                       'criteria': '==',
                                       'value':    '"+1"',
                                       'format':   my_format2})

# Close the file.
workbook.close()




# csv_columns = ['date',0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
# csv_file = "data2.csv"
# try:
#     with open(csv_file, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         writer.writeheader()
#         for row in (dict(zip(csv_columns, item)) for item in res.items()):
#             writer.writerow(row)
# except IOError:
#     print("I/O error")






"""
# Fixing random state for reproducibility
np.random.seed(19680801)


plt.rcdefaults()
fig, ax = plt.subplots()

# Example data
# people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
date = [i['date_in'] for i in list_of_trades]
y_pos = np.arange(len(date))
time_delta = [(i['date_out'] - i['date_in']).total_seconds() for i in list_of_trades]
time_delta_profit = [i['profit'] for i in list_of_trades]
performance = time_delta
error = np.random.rand(len(date))

ax.barh(y_pos, performance, xerr=error, align='center')
for i, v in enumerate(time_delta):
    ax.text(v+50,
            i + -0.125,
            str(v)+' mins, prft: '+time_delta_profit[i],
            color='red' if float(time_delta_profit[i]) < 0 else 'green',
            # fontweight='bold',
            fontsize="8"
            )

ax.set_yticks(y_pos)
ax.set_yticklabels(date)
# ax.invert_yaxis()  # labels read top-to-bottomR

ax.set_xlabel('Trade in minutes')
ax.set_title('Trade Time')

plt.show()
"""
"""
countries = ['USA', 'GB', 'China', 'Russia', 'Germany']
bronzes = np.array([38, 17, 26, 19, 15])
silvers = np.array([37, 23, 18, 18, 10])
golds = np.array([46, 27, 26, 19, 17])
ind = [x for x, _ in enumerate(countries)]

plt.bar(ind, golds, width=0.8, label='golds', color='gold', bottom=silvers+bronzes)
plt.bar(ind, silvers, width=0.8, label='silvers', color='silver', bottom=bronzes)
plt.bar(ind, bronzes, width=0.8, label='bronzes', color='#CD853F')

plt.xticks(ind, countries)
plt.ylabel("Medals")
plt.xlabel("Countries")
plt.legend(loc="upper right")
plt.title("2012 Olympics Top Scorers")

plt.show()
"""