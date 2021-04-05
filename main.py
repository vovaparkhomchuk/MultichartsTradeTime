import os
import csv
from start import start
from functions import init_real_list_of_trades
from db import get_orders_from_db

REAL_ORDERS = False
BACKTEST = True
PORTFOLIO = False
os.system("sudo rm -rf AnalysisMaterials")
os.system("sudo mkdir AnalysisMaterials")

coins = {
    'EPZ20': 'S&P500',
    'GCEZ20': 'Gold',
    'ENQZ20': 'Nasdaq',
}
if REAL_ORDERS:
    print("REAL ORDERS")
    user = "VVM"
    ticker = 'MNQ'
    list_of_trades = get_orders_from_db(user=user, ticker=ticker)
    start(real_orders=REAL_ORDERS, backtest=True, input_file=list_of_trades, coin=ticker)
elif BACKTEST:
    os.system("sudo rm -rf plots")
    os.system("sudo mkdir plots")
    coin = "Den_Bug"
    with open(f"{coin}.csv") as f: input_file = list(csv.DictReader(f, delimiter=";"))
    start(real_orders=None, backtest=BACKTEST, input_file=input_file, coin=coin)
else:
    with open("Portfolio_for_Max_Real.csv") as f: orders_raw = list(csv.DictReader(f, delimiter=";"))
    arr = []
    for i in orders_raw:
        if i['Profile'] != 'Paper Trader':
            arr.append(i)
    orders_raw = arr
    # print(orders_raw)
    # exit()
    orders_raw.reverse()
    orders_correct = init_real_list_of_trades(orders_raw)
    for coin in orders_correct:

        os.system("sudo rm -rf plots")
        os.system("sudo mkdir plots")
        start(real_orders=None, backtest=BACKTEST, input_file=orders_correct, coin=coins[coin], portfolio=PORTFOLIO)

exit()
