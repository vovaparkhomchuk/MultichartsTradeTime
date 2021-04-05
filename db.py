import mysql.connector
import datetime


mydb = mysql.connector.connect(
    host="ibeumax.mysql.tools",
    user="ibeumax_orders",
    password="v5J+g5g#6R",
    database="ibeumax_orders"
)


def get_orders_from_db(user=None, ticker=None):
    mycursor = mydb.cursor()
    print(f"SELECT * FROM orders WHERE user='{user}' AND ticker='{ticker}' ORDER BY opentime ASC")
    # mycursor.execute(f"SELECT * FROM orders WHERE user='{user}' AND ticker='{ticker}' ORDER BY opentime ASC")
    mycursor.execute(f"SELECT * FROM orders WHERE user='{user}' ORDER BY opentime ASC")
    myresult = mycursor.fetchall()
    list_of_trades = []
    for x in myresult:
        # print(x)
        trade = {
          "date_in": datetime.datetime.fromtimestamp(x[1]),
          "date_out": datetime.datetime.fromtimestamp(x[2]),
          "price_in": x[3],
          "price_out": x[4],
          "profit": str(x[4] * x[5] - x[3] * x[5]) if x[8] == 'l' else str(x[3] * x[5] - x[4] * x[5]),
          "type": "long" if x[8] == 'l' else "short",
          "instrument": x[7]
        }
        list_of_trades.append(trade)
        # print(trade)
    #
    # exit()
    return list_of_trades

def order_to_csv(user=None):
    if user is not None:
        orders = get_orders_from_db(user=user)

        print(orders)
        import csv
        keys = orders[0].keys()
        with open(f'{user}_Real.csv', 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(orders)

order_to_csv('VVM')