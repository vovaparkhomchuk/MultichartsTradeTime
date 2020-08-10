from datetime import timedelta
import xlsxwriter
import datetime
import csv

FORMAT_DATE = '%m/%d/%y %I:%M:%S %p'
number = 41333.5

with open("ExampleIn.csv") as f:
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
    # if i.weekday() == 5 or i.weekday() == 6:
    #     i = i.strftime('%Y/%m/%d')+"-wknd"
    res[i] = ["" for j in hours]

# print(days)
# exit()

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
        # print(val)
        if float(profits[k]) > 0:
            res[val.date()][val.hour] = "+prof {}".format(types[k][0])
            # res[val.date()][val.hour] = "+1"
        else:
            res[val.date()][val.hour] = "-prof {}".format(types[k][0])
            # res[val.date()][val.hour] = "-1"



# exit()
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
        # print(day)
        if day.weekday() == 4:
            print(day)
            for j in range(17, 25):
                v[j] = 'wknd'
                # print(v[j])
        elif day.weekday() == 5:
            for j in range(1, 25):
                v[j] = 'wknd'
                # print(v[j])
        elif day.weekday() == 6:
            for j in range(1, 18):
                v[j] = 'wknd'
                # print(v[j])
# exit()


workbook = xlsxwriter.Workbook('result.xlsx')
worksheet = workbook.add_worksheet()
prof_minus = workbook.add_format({'bg_color': '#FFC7CE'})
prof_plus = workbook.add_format({'bg_color': '#00ff80'})
weekend = workbook.add_format({'bg_color': '#34cceb'})

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
