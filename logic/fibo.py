import numpy as np
import pandas as pd
from database.operation import find_all_klines, find_strategy_users_id
from project_types.types import KlineFind
from bot.messager import send


def zigzag(symbol: str, timeframe: str, period: int):
    data = find_all_klines(KlineFind(symbol=symbol, time_frame=timeframe, quantity=1000))
    df = pd.DataFrame(list(data))
    df['ph'] = df['high'].rolling(period).max().fillna(0).shift() < df['high']
    df['pl'] = df['low'].rolling(period).min().fillna(0).shift() > df['low']
    df['sum_ph'] = df['ph'].rolling(period).sum().shift(-period)
    df['sum_pl'] = df['pl'].rolling(period).sum().shift(-period)
    df['buy'] = None
    df['sell'] = None
    df.reset_index()
    df['status'] = None
    for index, item in df.iterrows():
        if item['pl'] and item['sum_pl'] == 0:
            df.loc[index, "buy"] = True
        if item['ph'] and item['sum_ph'] == 0:
            df.loc[index, "sell"] = True
        if df.loc[index, "buy"] or df.loc[index, "sell"]:
            df.loc[index, 'status'] = 'buy' if df.loc[index, "buy"] else "sell" if df.loc[
                index, "sell"] else None
        else:
            df.loc[index, 'status'] = df['status'].iloc[index - 1]
    df = df.drop(["sum_pl", "sum_ph", "volume", "buy", "sell"], axis=1)

    df['open'] = np.log10(df['open'])
    df['close'] = np.log10(df['close'])
    df['high'] = np.log10(df['high'])
    df['low'] = np.log10(df['low'])

    return df


def fibo_retracement(symbol: str, timeframe: str, period: int = 10):
    users_id = find_strategy_users_id('fibo', timeframe, symbol)
    if users_id:
        df = zigzag(symbol, timeframe, period)
        status = df.iloc[-1]["status"]
        close_price = df.iloc[-1]["close"]
        close_price1 = df.iloc[df.shape[0] - 2]["close"]
        high_low_dict = {"high_this": 0, "low_this": 0, "high_last": 0, "low_last": 0}
        for index in reversed(df.index):
            if df.iloc[index]['status'] == status:
                if high_low_dict["high_this"] == 0 and df.iloc[index]['ph']:
                    high_low_dict['high_this'] = df.iloc[index]['high']
                elif high_low_dict["low_this"] == 0 and df.iloc[index]['pl']:
                    high_low_dict['low_this'] = df.iloc[index]['low']
            elif df.iloc[index]['status'] != status:
                if high_low_dict["high_last"] == 0 and df.iloc[index]['ph']:
                    high_low_dict['high_last'] = df.iloc[index]['high']
                elif high_low_dict["low_last"] == 0 and df.iloc[index]['pl']:
                    high_low_dict['low_last'] = df.iloc[index]['low']
            elif 0 not in high_low_dict.values():
                break

        if status == "buy":
            if close_price * 2 < close_price1 * 2 < high_low_dict["low_this"] + high_low_dict[
                "high_this"] and close_price1 * 2 < close_price * 2 < high_low_dict["low_this"] + high_low_dict[
                "high_this"]:
                for user in users_id:
                    send(user, fib_message(symbol, timeframe, False))
            elif close_price * 2 > high_low_dict["low_last"] + high_low_dict["high_last"] > close_price1 * 2:
                for user in users_id:
                    send(user, fib_message(symbol, timeframe, True))

        elif status == "sell":
            if close_price * 2 > close_price1 * 2 > high_low_dict["low_this"] + high_low_dict[
                "high_this"] and close_price1 * 2 > close_price * 2 > high_low_dict["low_this"] + high_low_dict[
                "high_this"]:
                for user in users_id:
                    send(user, fib_message(symbol, timeframe, True))

            elif close_price * 2 < high_low_dict["low_last"] + high_low_dict["high_last"] < close_price1 * 2:
                for user in users_id:
                    send(user, fib_message(symbol, timeframe, False))


def fib_message(sym: str, tf: str, direction: bool) -> str:
    if direction:
        return f"🚨 FIBONACCI ALERT 🚨\n🟢CROSSING UP🟢\nsymbol: {sym},\ntime frame: {tf}"
    else:
        return f"🚨 FIBONACCI ALERT 🚨\n🔴CROSSING DOWN🔴\nsymbol: {sym},\ntime frame: {tf}"
