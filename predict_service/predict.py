from tvDatafeed import TvDatafeed, Interval
import datetime;

def get_curr_position(curr_short, curr_mid, curr_long):
    if (curr_short > curr_mid) and (curr_mid > curr_long):
        curr_position = 1
    elif (curr_short < curr_mid) and (curr_mid < curr_long):
        curr_position = 0
    return curr_position;

def basic_predict(symbol, exchange, time_frame, short_ma = 5, mid_ma = 20, long_ma = 50):
    tv = TvDatafeed()
    interval = {
        1: Interval.in_1_minute,
        3: Interval.in_3_minute,
        5: Interval.in_5_minute,
        15: Interval.in_15_minute,
        30: Interval.in_30_minute,
        45: Interval.in_45_minute,
        60: Interval.in_1_hour,
        120: Interval.in_2_hour,
        180: Interval.in_3_hour,
        240: Interval.in_4_hour,
        2400: Interval.in_daily,
    }
    #Let's get some data
    # stock_data = tv.get_hist(symbol=symbol,exchange='SET',interval=Interval.in_1_hour,n_bars=5000)
    btc_usd_data=tv.get_hist(symbol, exchange, interval.get(time_frame), n_bars=5000)
    result_log = {
        "predictable" : True,
        "symbol": symbol,
        "exchange": exchange,
        "type": None,
        "at_price": None,
        "at_time": None,
        "executed_at": datetime.datetime.now()
    }
    #create moving average
    short_ma = 5
    mid_ma = 20
    long_ma = 50
    
    btc_usd_data[f'{short_ma}MA'] = btc_usd_data['close'].rolling(short_ma).mean()
    btc_usd_data[f'{mid_ma}MA'] = btc_usd_data['close'].rolling(mid_ma).mean()
    btc_usd_data[f'{long_ma}MA'] = btc_usd_data['close'].rolling(long_ma).mean()

    btc_usd_data['signal'] = 0

    last_curr_short = btc_usd_data[f'{short_ma}MA'].iloc[-2]
    last_curr_mid = btc_usd_data[f'{mid_ma}MA'].iloc[-2]
    last_curr_long = btc_usd_data[f'{long_ma}MA'].iloc[-2]
    last_curr_position = get_curr_position(last_curr_short, last_curr_mid, last_curr_long)
    
    curr_short = btc_usd_data[f'{short_ma}MA'].iloc[-1]
    curr_mid = btc_usd_data[f'{mid_ma}MA'].iloc[-1]
    curr_long = btc_usd_data[f'{long_ma}MA'].iloc[-1]
    curr_position = get_curr_position(curr_short, curr_mid, curr_long)
    
    if (curr_position == 1):
        if (last_curr_position == 0):
            result_log["type"] = "buy"
        else:
            result_log["type"] = "hold"
    elif (curr_position == 0):
        if (last_curr_position == 1):
            result_log["type"] = "sell"
        else:
            result_log["type"] = "unhold"
    else:
        result_log["predictable"] = False;
        
    return (result_log)

print(basic_predict("BTCUSDT", "BINANCE", 60))