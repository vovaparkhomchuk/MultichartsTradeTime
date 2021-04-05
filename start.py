import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from datetime import timedelta
from PyPDF2 import PdfFileWriter, PdfFileReader
from functions import init_list_of_trades, get_trading_days, get_blank_result, get_trades_info, \
    get_trades_like_calendar, plot_res, get_results, create_calendar_html, get_equity, plot_equity_and_drawdown, \
    get_drawdown, get_general_statistics, init_real_list_of_trades

coins = {
    'EPZ20': 'S&P500',
    'GCEZ20': 'Gold',
    'ENQZ20': 'Nasdaq',
    'GCEG21': 'Gold',
    'CLEF21': "Crude Oil",
    'NQMG21': "Crude Oil",
    'ENQH21': "Nasdaq",
    'MESZ20': 'S&P500',
    'MNQZ20': 'Nasdaq',
    'MGCZ20': 'Gold',
    'MGCG21': 'Gold',
    'MESH21': 'S&P500',
    'MNQH21': 'Nasdaq',
}

def start(real_orders=None, backtest=None, input_file=None, coin=None, portfolio=None):
    coin_stat = {}
    """
        list_of_trades fields:
        - date_in
        - date_out
        - price_in
        - price_out
        - profit
        - type
        """
    if real_orders:
        list_of_trades = input_file
        backtest = False
    elif backtest:
        list_of_trades = init_list_of_trades(input_file)
        # print(list_of_trades)
        # temp = []
        # for i in list_of_trades:
        #     if i['date_in'].hour != 2 and i['date_in'].hour != 9 and i['date_in'].hour != 10 and i['date_in'].hour != 11:
        #         temp.append(i)
        # list_of_trades = temp
        # exit()
    else:
        if portfolio:
            # exit()
            list_of_trades = []
            for coin in input_file:
                if coin[0] != "M" or True:
                    print(coin)
                    coin_stat[coin] = {
                        'profit': 0,
                        'deals': 0,
                        'max_drawdown': 0,
                    }
                    for deal in input_file[coin]:
                        coin_stat[coin]['profit'] += float(deal['profit'])
                        coin_stat[coin]['deals'] += 1
                        deal['instrument'] = coins[coin]
                        deal['date_in'] = deal['date_in'] # - timedelta(hours=7)
                        deal['date_out'] = deal['date_out'] # - timedelta(hours=7)
                        list_of_trades.append(deal)

                    trading_days = get_trading_days(input_file[coin])
                    real_equity = get_equity(input_file[coin], trading_days)
                    drawdown = get_drawdown(real_equity, trading_days)
                    max_drawdown = 0
                    for i in drawdown:
                        if i[1] < max_drawdown:
                            max_drawdown = i[1]
                    coin_stat[coin]['max_drawdown'] = max_drawdown
                    print(max_drawdown)

            coin = 'Portfolio'
            list_of_trades = sorted(list_of_trades, key=lambda i: i['date_in'])
            for i in list_of_trades:
                print(i)
            # exit()
        else:
            list_of_trades = input_file[coin]


    # print(coin_stat)
    # exit()

    trading_days = get_trading_days(list_of_trades)
    blank_result_list, blank_result_dict = get_blank_result(trading_days)
    date_ins, profits, types = get_trades_info(list_of_trades)
    trades_like_calendar, trades_like_calendar_for_excel = get_trades_like_calendar(date_ins, blank_result_dict,
                                                                                    profits,
                                                                                    types)

    real_equity = get_equity(list_of_trades, trading_days)
    drawdown = get_drawdown(real_equity, trading_days)
    plot_equity_and_drawdown(real_equity, drawdown)



    general_statistics = get_general_statistics(list_of_trades, drawdown, real_equity)

    x = 380
    y = 350
    font_head = ImageFont.truetype("Montserrat_SemiBold.ttf", 120)
    font = ImageFont.truetype("Montserrat_Medium.ttf", 80)
    font2 = ImageFont.truetype("Hack-Regular.ttf", 65)
    img = Image.new("RGBA", (3200, 2650), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((x, 150), f"Statistics: (c {trading_days[0]} по {trading_days[-1]})", (255, 255, 255), font=font_head)
    ind = 0
    for i in general_statistics:
        # text = i.capitalize().replace('_', ' ') + ": " + (str('{:.1f}'.format(general_statistics[i])) if ind > 2 else str('{:.0f}'.format(general_statistics[i])))
        text = i.capitalize().replace('_', ' ') + ": " + str('{:.1f}'.format(general_statistics[i]))
        draw.text((x, y), text, (255, 255, 255), font=font)
        y += 170
        ind += 1
    y += 100
    if not backtest and portfolio and False:
        for i in coin_stat:
            text = coins[i].ljust(10) + \
                   ("Profit: " + str(coin_stat[i]['profit'])).ljust(18) + \
                   ("Deals: " + str(coin_stat[i]['deals'])).ljust(12) + \
                   ("Max drawdown: " + str(coin_stat[i]['max_drawdown'])).ljust(18)
            draw.text((x, y), text, (255, 255, 255), font=font2)
            y += 170
            ind += 1
        draw = ImageDraw.Draw(img)

    img.save("plots/z_stat.png")

    x = 380
    y = 350
    height = 350
    for i in list_of_trades:
        height += 120
    font_head = ImageFont.truetype("Montserrat_SemiBold.ttf", 120)
    font = ImageFont.truetype("Hack-Regular.ttf", 50)
    img = Image.new("RGBA", (3200, height + 250), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((x, 150), "List of orders:", (255, 255, 255), font=font_head)
    ind = 0
    text = "{:<15}".format("Instrument") + \
           "{:<25}".format("Date in ") + \
           "{:<25}".format("Date out ") + \
           "{:<25}".format("Profit ($) ")

    draw.text((x, y), text, (255, 255, 255), font=font)
    y += 120
    if not backtest:
        for i in list_of_trades:
            text = "{:<15}".format(str(i['instrument'])) + \
                   "{:<25}".format(str(i['date_in'].date())) + \
                   "{:<25}".format(str(i['date_out'].date())) + \
                   "{:<25}".format(str(i['profit']))
            draw.text((x, y), text, (255, 255, 255), font=font)
            y += 120
            ind += 1
        draw = ImageDraw.Draw(img)

        img.save("plots/0_list_of_orders.png")

    # exit()

    # exit()
    create_calendar_html(trades_like_calendar_for_excel, coin)

    list_of_profit_trades_at_time, \
    list_of_unprofit_trades_at_time, \
    list_of_profit_trades_at_time_out, \
    list_of_unprofit_trades_at_time_out, \
    list_of_profit_trades_at_time_with_prof, \
    list_of_unprofit_trades_at_time_with_prof, \
    list_of_profit_trades_at_time_out_with_prof, \
    list_of_unprofit_trades_at_time_out_with_prof, \
    list_of_profit_trades_at_time_with_hours, \
    list_of_unprofit_trades_at_time_with_hours, \
    list_of_net_profit_trades_at_time_with_prof, \
    list_of_net_profit_trades_at_time_out_with_prof = get_results(list_of_trades)

    results_dict = [
        [list_of_profit_trades_at_time, list_of_unprofit_trades_at_time],
        [list_of_profit_trades_at_time_out, list_of_unprofit_trades_at_time_out],
        [list_of_profit_trades_at_time_with_prof, list_of_unprofit_trades_at_time_with_prof,
         list_of_net_profit_trades_at_time_with_prof],
        [list_of_profit_trades_at_time_out_with_prof, list_of_unprofit_trades_at_time_out_with_prof,
         list_of_net_profit_trades_at_time_out_with_prof],
        # [list_of_profit_trades_at_time_with_hours, list_of_unprofit_trades_at_time_with_hours],
    ]
    for k, v in enumerate(results_dict):
        plot_res(v[0], v[1], k, results_dict)

    plots = sorted(os.listdir('./plots'))
    image_list = []
    img = None
    for i in plots:
        if ".png" in i:
            image = Image.open('./plots/' + i)
            img = image.convert('RGB')
            image_list.append(img)
    img.save(f'AnalysisMaterials/Plots-{coin}.pdf', save_all=True, append_images=image_list)

    pages_to_keep = range(1, len(plots))
    infile = PdfFileReader(f'AnalysisMaterials/Plots-{coin}.pdf', 'rb')
    output = PdfFileWriter()
    p = infile.getPage(len(plots))
    output.addPage(p)
    for i in pages_to_keep:
        p = infile.getPage(i)
        output.addPage(p)
    with open(f'AnalysisMaterials/Plots-{coin}.pdf', 'wb') as f:
        output.write(f)

    if portfolio:
        exit()