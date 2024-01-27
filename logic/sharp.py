from database.operation import find_last_kline, find_strategy_users_id
from project_types.types import KlineFind
from bot.messager import send


def sharp_finder(symbol: str, time_frame: str, sharp_count: int = 3):
    users_id = find_strategy_users_id('sharp', time_frame, symbol)
    if users_id:
        decide_list = []
        candles = find_last_kline(KlineFind(symbol=symbol, time_frame=time_frame, quantity=sharp_count))
        for candle in candles:
            if candle['close'] > candle['open']:
                decide_list.append('long')
            elif candle['close'] < candle['open']:
                decide_list.append('short')
            else:
                decide_list.append('neutral')
        if set(decide_list) == {"short"}:
            users_id = find_strategy_users_id('sharp', time_frame, symbol)
            for user in users_id:
                send(user, f"🚨 SHARP ALERT 🚨\n🔴SHORT🔴\nsymbol: {symbol},\ntime frame: {time_frame}")
        elif set(decide_list) == {"long"}:
            users_id = find_strategy_users_id('sharp', time_frame, symbol)
            for user in users_id:
                send(user, f"🚨 SHARP ALERT 🚨\n🟢LONG🟢\nsymbol: {symbol},\ntime frame: {time_frame}")
