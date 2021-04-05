import datetime
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta


matplotlib.use('agg')
plt.rcParams.update({'font.size': 5})


def init_real_list_of_trades(orders_raw):
    FORMAT_DATE = '%m/%d/%Y %I:%M:%S %p'
    orders_temp = {}
    orders_correct = {}
    for i in orders_raw:
        if i['Position'] == "Long":
            orders_temp[i['Instrument']] = {
                'date_in': datetime.datetime.strptime(i['Date/Time'], FORMAT_DATE),
                'date_out': '',
                'price_in': i['Average Price'],
                'price_out': 0,
                'profit': 0,
                'type': 'long'
            }
        if i['Position'] == "Short":
            orders_temp[i['Instrument']] = {
                'date_in': datetime.datetime.strptime(i['Date/Time'], FORMAT_DATE),
                'date_out': '',
                'price_in': i['Average Price'],
                'price_out': 0,
                'profit': 0,
                'type': 'short'
            }
        if i['Position'] == "Flat":
            if i['Instrument'] in orders_temp:
                orders_temp[i['Instrument']]['date_out'] = datetime.datetime.strptime(i['Date/Time'], FORMAT_DATE)
                orders_temp[i['Instrument']]['profit'] = i['Realized P/L'].replace("$", "").replace(" ", "").replace(
                    ",", "")
                if i['Instrument'] not in orders_correct:
                    orders_correct[i['Instrument']] = []
                orders_correct[i['Instrument']].append(orders_temp[i['Instrument']])
                orders_temp.pop(i['Instrument'])
    return orders_correct

def init_list_of_trades(input_file):
    format_date = '%m/%d/%y %I:%M:%S %p'
    list_of_trades = []
    for i in range(len(input_file)):
        if input_file[i]['Profit ($)']:
            date_out = datetime.datetime.strptime(str(input_file[i + 1]['Date']) + ' ' +
                                                  str(input_file[i + 1]['Time']), format_date)
            date_in = datetime.datetime.strptime(str(input_file[i]['Date']) + ' ' +
                                                 str(input_file[i]['Time']), format_date)
            trade = {
                "date_in": date_in,
                "date_out": date_out,
                "price_in": input_file[i]['Price'],
                "price_out": input_file[i + 1]['Price'],
                "profit": input_file[i]['Profit ($)'],
                "type": "long" if input_file[i + 1]['Type'] == "ExitLong" else "short"
            }
            list_of_trades.append(trade)
    return list_of_trades


def get_trading_days(list_of_trades):
    days = []
    day_start = list_of_trades[0]['date_in'].date()
    # print(type(list_of_trades[len(list_of_trades) - 1]['date_out']))
    day_end = list_of_trades[len(list_of_trades) - 1]['date_out'].date()
    delta = day_end - day_start
    for i in range(delta.days + 1):
        day = day_start + timedelta(days=i)
        normal_date = day.strftime('%m/%d/%Y')
        days.append(day)
    return days


def get_blank_result(days):
    res = {}
    result = []
    hours = list(range(0, 24))
    for i in days:
        res[i] = ["" for j in hours]
    return result, res


def get_trades_like_calendar(trade_hours, blank_dict, profits, types):
    for k, v in enumerate(trade_hours):
        for i, val in enumerate(v):
            if float(profits[k].replace(',', '.')) > 0:
                blank_dict[val.date()][val.hour] = "+prof {}".format(types[k][0])
            else:
                blank_dict[val.date()][val.hour] = "-prof {}".format(types[k][0])
    result = [['date', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]]
    for i, val in enumerate(blank_dict):
        day = [str(val)]
        for hour in blank_dict[val]:
            day.append(hour)
        result.append(day)
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
    return blank_dict, result


def get_trades_info(list_of_trades):
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
    return trade_hours, profits, types


def get_general_statistics(list_of_trades, drawdown_list, equity_list):
    general_statistics = {
        'profit': equity_list[-1][1],
        'max_drawdown': 0,
        'number_of_trades': len(list_of_trades),
        'number_of_long_trades': 0,
        'number_of_short_trades': 0,
        'average_trade_time': 0,
        'average_profit_per_trade': 0,
        'average_loss_per_trade': 0
    }
    net_profit = 0
    drawdown = 0
    gross_profit = 0
    number_of_profit_trades = 0
    gross_loss = 0
    number_of_loss_trades = 0
    total_trade_time = datetime.timedelta(seconds=0)
    for i in list_of_trades:
        if i['type'] == 'long':
            general_statistics['number_of_long_trades'] += 1
        else:
            general_statistics['number_of_short_trades'] += 1
        profit = float(i['profit'].replace(',', '.'))
        net_profit += profit
        if profit >= 0:
            gross_profit += profit
            number_of_profit_trades += 1
        else:
            gross_loss += profit
            number_of_loss_trades += 1
        total_trade_time += i['date_out'] - i['date_in']
    if number_of_profit_trades > 0:
        general_statistics['average_profit_per_trade'] = gross_profit / number_of_profit_trades
    if number_of_loss_trades > 0:
        general_statistics['average_loss_per_trade'] = gross_loss / number_of_loss_trades
    general_statistics['average_trade_time'] = ((total_trade_time / general_statistics['number_of_trades']).seconds / 60) / 60
    for i in drawdown_list:
        if i[1] < drawdown:
            drawdown = i[1]
    general_statistics['max_drawdown'] = drawdown
    return general_statistics


def get_equity(list_of_trades, trading_days):
    equity = 0
    date = None
    arr = []
    for i in list_of_trades:
        current_date = str(i['date_in'].day) + "/" + str(i['date_in'].month) + "/" + str(i['date_in'].year)
        profit = float(i['profit'].replace(',', '.'))
        if date is None:
            date = current_date
            equity += profit
        else:
            if date == current_date:
                equity += profit
            else:
                arr.append(
                    {date: equity}
                )
                date = current_date
                equity += profit
    arr.append(
        {date: equity}
    )
    real_equity = []
    for i in trading_days:
        real_equity.append([i, 0])
    last_equity = 0
    for i in real_equity:
        for j in arr:
            for day in j:
                trading_days_day = str(i[0].day) + "/" + str(i[0].month) + "/" + str(i[0].year)
                if trading_days_day == day:
                    i[1] = j[day]
                    last_equity = j[day]
                    continue
                i[1] = last_equity
    return real_equity


def plot_equity_and_drawdown(real_equity, real_drawdown):
    ind = np.arange(5)  # the x locations for the groups
    width = 0.35
    x = [i[0] for i in real_equity]
    y = [i[1] for i in real_equity]
    y2 = [i[1] for i in real_drawdown]
    fig, ax = plt.subplots()
    ax.set_title("Equity/Drawdown")
    # ax.set_xticks(x)
    ax.bar(x, y, label='Equity', color=(0.1, 0.6, 0.4))
    ax.bar(x, y2, label='Drawdown', color=(0.9, 0.2, 0.4))
    ax.legend()
    plt.show()
    plt.savefig("./plots/1_equity.png", dpi=500)


def get_drawdown(real_equity, trading_days):
    real_drawdown = []
    last_drawdown = 0
    equity = 0
    started = False
    for i in trading_days:
        real_drawdown.append([i, 0])
    for i, val in enumerate(real_equity):
        date = val[0]
        equity = val[1]
        if i > 0:
            if equity < real_equity[i-1][1] and not started:
                # print(equity, real_equity[i-1][1])
                last_drawdown = equity - real_equity[i-1][1]
                real_drawdown[i][1] = last_drawdown
                started = True
            else:
                last_drawdown += equity - real_equity[i - 1][1]
                if last_drawdown > 0:
                    real_drawdown[i][1] = 0
                    last_drawdown = 0
                elif last_drawdown == 0:
                    last_drawdown = equity - real_equity[i - 1][1]
                    real_drawdown[i][1] = last_drawdown
                else:
                    real_drawdown[i][1] = last_drawdown
    return real_drawdown


def get_results(list_of_trades):
    hours = list(range(0, 24))

    list_of_net_profit_trades_at_time = {}
    list_of_profit_trades_at_time = {}
    list_of_unprofit_trades_at_time = {}

    list_of_net_profit_trades_at_time_out = {}
    list_of_profit_trades_at_time_out = {}
    list_of_unprofit_trades_at_time_out = {}

    list_of_net_profit_trades_at_time_with_prof = {}
    list_of_profit_trades_at_time_with_prof = {}
    list_of_unprofit_trades_at_time_with_prof = {}

    list_of_net_profit_trades_at_time_out_with_prof = {}
    list_of_profit_trades_at_time_out_with_prof = {}
    list_of_unprofit_trades_at_time_out_with_prof = {}

    list_of_net_profit_trades_at_time_with_hours = {}
    list_of_profit_trades_at_time_with_hours = {}
    list_of_unprofit_trades_at_time_with_hours = {}

    average_profit_per_trade_hour_prof = {}
    average_profit_per_trade_hour_unprof = {}
    for i in hours:
        list_of_profit_trades_at_time[i] = 0
        list_of_unprofit_trades_at_time[i] = 0
        list_of_profit_trades_at_time_out[i] = 0
        list_of_unprofit_trades_at_time_out[i] = 0

        list_of_net_profit_trades_at_time_with_prof[i] = 0
        list_of_profit_trades_at_time_with_prof[i] = 0
        list_of_unprofit_trades_at_time_with_prof[i] = 0

        list_of_net_profit_trades_at_time_out_with_prof[i] = 0
        list_of_profit_trades_at_time_out_with_prof[i] = 0
        list_of_unprofit_trades_at_time_out_with_prof[i] = 0

        list_of_profit_trades_at_time_with_hours[i] = 0
        list_of_unprofit_trades_at_time_with_hours[i] = 0
    iter = 0
    for i in list_of_trades:
        # if i['date_out'].weekday() < i['date_in'].weekday() or i['date_out'].weekday() == 6:
        #     continue
        # if iter <= 2:
        #     iter += 1
        #     continue
        list_of_net_profit_trades_at_time_with_prof[i['date_in'].hour] += float(i['profit'].replace(',', '.'))
        list_of_net_profit_trades_at_time_out_with_prof[i['date_out'].hour] += float(i['profit'].replace(',', '.'))

        if float(i['profit'].replace(',', '.')) > 0:
            list_of_profit_trades_at_time[i['date_in'].hour] += 1
            list_of_profit_trades_at_time_out[i['date_out'].hour] += 1
            list_of_profit_trades_at_time_with_prof[i['date_in'].hour] += float(i['profit'].replace(',', '.'))
            list_of_profit_trades_at_time_out_with_prof[i['date_out'].hour] += float(i['profit'].replace(',', '.'))

            delta = i['date_out'] - i['date_in']
            days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
            total = (days * 24 * 60 + hours * 60 + minutes) / 60
            list_of_profit_trades_at_time_with_hours[i['date_in'].hour] += total

            if total in average_profit_per_trade_hour_prof.keys():
                average_profit_per_trade_hour_prof[round(total)].append(float(i['profit'].replace(',', '.')))
            else:
                average_profit_per_trade_hour_prof[round(total)] = [float(i['profit'].replace(',', '.'))]
        else:
            list_of_unprofit_trades_at_time[i['date_in'].hour] += 1
            list_of_unprofit_trades_at_time_out[i['date_out'].hour] += 1
            list_of_unprofit_trades_at_time_with_prof[i['date_in'].hour] += float(i['profit'].replace(',', '.'))
            list_of_unprofit_trades_at_time_out_with_prof[i['date_out'].hour] += float(i['profit'].replace(',', '.'))

            delta = i['date_out'] - i['date_in']
            days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
            total = (days * 24 * 60 + hours * 60 + minutes) / 60
            list_of_unprofit_trades_at_time_with_hours[i['date_in'].hour] += total

            if total in average_profit_per_trade_hour_unprof.keys():
                average_profit_per_trade_hour_unprof[round(total)].append(float(i['profit'].replace(',', '.')))
            else:
                average_profit_per_trade_hour_unprof[round(total)] = [float(i['profit'].replace(',', '.'))]
    return [list_of_profit_trades_at_time, list_of_unprofit_trades_at_time, list_of_profit_trades_at_time_out,
            list_of_unprofit_trades_at_time_out, list_of_profit_trades_at_time_with_prof,
            list_of_unprofit_trades_at_time_with_prof, list_of_profit_trades_at_time_out_with_prof,
            list_of_unprofit_trades_at_time_out_with_prof, list_of_profit_trades_at_time_with_hours,
            list_of_unprofit_trades_at_time_with_hours,
            list_of_net_profit_trades_at_time_with_prof,
            list_of_net_profit_trades_at_time_out_with_prof]


def plot_res(prof, unprof, ind, res_list):
    labels = list(range(0, 24))
    if ind == 4:
        profit_bar = [round(prof[i] / res_list[0][0][i] if res_list[0][0][i] != 0 else 1) for i in prof]
        unprofit_bar = [round(unprof[i] / res_list[0][1][i] if res_list[0][1][i] != 0 else 1) for i in unprof]
    elif ind == 2 or ind == 3:
        net_profit_bar = [(0 if (res_list[ind][2][i] == prof[i] or res_list[ind][2][i] == unprof[i]) else res_list[ind][2][i]) for i in res_list[ind][2]]
        profit_bar = [prof[i] for i in prof]
        unprofit_bar = [unprof[i] for i in unprof]
    else:
        profit_bar = [prof[i] for i in prof]
        unprofit_bar = [unprof[i] for i in unprof]

    x = np.arange(len(labels))  # the label locations
    width = 0.4  # the width of the bars
    fig, ax = plt.subplots()
    rects_1 = ax.bar(x - width / 2, profit_bar, width, label='Profit', color=(0.1,0.6,0.4))
    rects_2 = ax.bar(x + width / 2, unprofit_bar, width, label='Loss', color=(0.9,0.2,0.4))
    if ind == 2 or ind == 3:
        rects_3 = ax.bar(x + width / 2, net_profit_bar, width, label='Net', color=(0.2,0.4,0.9))

    titles = [
        'Кол-во сделок открытых в (...):',
        'Кол-во сделок закрытых в (...):',
        'Кол-во сделок открытых в (...) с профитом:',
        'Кол-во сделок закрытых в (...) с профитом:',
        'Кол-во сделок открытых в (...) с часами:',
    ]

    ax.set_ylabel('Scores')
    ax.set_title(titles[ind])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def auto_label(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    auto_label(rects_1)
    auto_label(rects_2)
    if ind == 2 or ind == 3:
        auto_label(rects_3)
    # fig.tight_layout()
    plt.savefig("./plots/"+str(ind+2)+".png", dpi=500)
    plt.close()


def create_calendar_html(trades_like_calendar_for_excel, coin):
    html = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>Таблица</title>
                <style type="text/css">
                   TABLE {
                    width: 300px; /* Ширина таблицы */
                    border-collapse: collapse; /* Убираем двойные линии между ячейками */
                   }
                   TD, TH {
                    padding: 3px; /* Поля вокруг содержимого таблицы */
                    border: 1px solid black; /* Параметры рамки */
                   }
                   TH {
                    //background: #b0e0e6; /* Цвет фона */
                    height:35px;
                   }
                   .red {
                    background-color: #f16b6b;
                   }
                </style>
            </head>
            <body>
                <table>\n"""
    for i in trades_like_calendar_for_excel:
        html += "<tr>\n"
        iter = 0
        for j in i:
            if "+prof" in str(j):
                html += "<th style='background-color: #78d278;'>" + str(j) + "</th>\n"
            elif "-prof" in str(j):
                html += "<th class='red'>" + str(j) + "</th>\n"
            elif "date" in str(j):
                html += "<th style='width: 80px; display: block;'>" + str(j) + "</th>\n"
            else:
                if iter == 0:
                    html += "<th style='width: 80px;'>" + str(j) + "</th>\n"
                else:
                    html += "<th>" + str(j) + "</th>\n"
            iter += 1
        html += "</tr>\n"
    html += """
                </table>
            </body>
        </html>"""

    f = open(f"AnalysisMaterials/Calendar-{coin}.html", "w")
    f.write(str(html))
    f.close()
