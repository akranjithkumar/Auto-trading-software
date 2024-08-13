import csv
import sys
import time
import logging
#logging.basicConfig(level=logging.DEBUG)
import numpy as np
from alphatrade import *
import pyotp
from colorama import Fore
money_per_line = 0
token = 0
base = 0
net_pos = 0
early_buy_tok = " "
early_sell_tok = " "
ini_price=0.0


def exit():
    pass
def soft_call():
    # login detail
    global money_per_line,token,base,net_pos,early_buy_tok,early_sell_tok,ini_price
    login_id = "AA464"
    password = "Akrs@1234"
    pin = pyotp.TOTP("JIWCHIU3HXJKORVA").now()
    totp = f"{int(pin):06d}" if len(pin) <= 5 else pin

    try:
        access_token1 = open('a_token.txt', 'r').read().rstrip()
    except Exception as e:
        print('Exception occurred :: {}'.format(e))
        access_token1 = None

    # sas initialisation

    sas = AlphaTrade(login_id=login_id, password=password, twofa=totp,
                     access_token=access_token1,master_contracts_to_download=['NSE'])

    filename = open('B_data.csv', 'r')
    file = csv.DictReader(filename)
    buy = []
    sell = []
    for col in file:
        buy.append(col['buy'])
        sell.append(col['sell'])
    _buy = list(map(float, buy))
    _sell = list(map(float, sell))
    res_buy = list(np.around(np.array(_buy), 1))
    res_sell = list(np.around(np.array(_sell), 1))
    tot_list = res_buy + res_sell
    print(res_buy)
    print(res_sell)


    def call_cancel_buy():
        if (early_buy_tok == " "):
            pass
        else:
            sas.cancel_order(early_buy_tok)
            print("Buy cancelled : " + early_buy_tok)
    def call_cancel_sell():
        if (early_sell_tok == " "):
            pass
        else:
            sas.cancel_order(early_sell_tok)
            print("Sell cancelled : " + early_sell_tok)
    def place_order(min_price, max_price,temp_val):
        global base,early_buy_tok,early_sell_tok,early_buy,early_sell
        divide_min = money_per_line / min_price
        min_share = int(base * round(divide_min / base))

        divide_max = money_per_line / max_price
        max_share = int(base * round(divide_max / base))
        print("Net position = " + str(net_pos))
        print(Fore.GREEN, "Buy Order placed at " + str(min_price) + " , Qty = " + str(min_share))
        print(Fore.RED, "Sell Order placed at " + str(max_price) + ", Qty = " + str(max_share))
        print(Fore.WHITE, "----------------------------------------------------")
        str_token=str(token)

        get_buy_tok=(sas.place_order(transaction_type=TransactionType.Buy,
                              instrument=sas.get_instrument_by_token('NSE', str_token),
                              quantity=min_share,
                              order_type=OrderType.Limit,
                              product_type=ProductType.Intraday,
                              price=min_price,
                              trigger_price=None,
                              stop_loss=None,
                              square_off=None,
                              trailing_sl=None,
                              is_amo=False))
        get_sell_tok=(sas.place_order(transaction_type=TransactionType.Sell,
                              instrument=sas.get_instrument_by_token('NSE', str_token),
                              quantity=max_share,
                              order_type=OrderType.Limit,
                              product_type=ProductType.Intraday,
                              price=max_price,
                              trigger_price=None,
                              stop_loss=None,
                              square_off=None,
                              trailing_sl=None,
                              is_amo=False))
        early_buy_tok = get_buy_tok["data"]["oms_order_id"]
        early_sell_tok = get_sell_tok["data"]["oms_order_id"]
        


    def call_place_order(temp_val):
        max_val = 10000000000000000000.0
        for a in tot_list:
            if (max_val > a and a > temp_val):
                max_val = a
        min_val = 0.0
        for i in tot_list:
            if (min_val < i and i < temp_val):
                min_val = i
        place_order(min_val, max_val,temp_val)

    ins_scrip = sas.get_instrument_by_token("NSE", token)
    print(str(ins_scrip)+ "\n")


    socket_opened = False

    def get_price_first():
        def event_handler_quote_update(message):
            global ltp
            ltp = message['ltp']
        def open_callback():
            global socket_opened
            socket_opened = True

        def run_strategy():
            global net_pos,temp_val
            sas.start_websocket(subscribe_callback=event_handler_quote_update,
                                socket_open_callback=open_callback,
                                run_in_background=True)
            sas.subscribe(ins_scrip, LiveFeedType.MARKET_DATA)
            i = 1
            while True:
                if (i == 1):
                    i = 2
                    pass
                elif(i==2):
                    temp_val = ltp
                    print("Initial price : " +str(temp_val))
                    i = 3
                    call_place_order(temp_val)
                    pass
                elif(i==3):
                    inp = ltp
                    if (inp > temp_val and (inp in tot_list)):
                        temp_val = inp
                        print(Fore.BLUE, "Sell order Completed at " + str(temp_val))
                        call_cancel_buy()
                        call_place_order(temp_val)
                    elif (inp < temp_val) and (inp in tot_list):
                        temp_val = inp
                        print(Fore.BLUE, "Buy order Completed at " + str(temp_val))
                        call_cancel_sell()
                        call_place_order(temp_val)
                    else:
                        pass
                else:
                    pass
                time.sleep(0.1)
        run_strategy()
    get_price_first()

