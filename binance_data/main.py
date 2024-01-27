from functools import cache
from binance import Client


@cache
def timeframe_to_timestamp_milliseconds(timeframe: str) -> int:
    time_dict = {"m": 1, "h": 60, "d": 1440, 'w': 10080}
    millisecond_timestamp_value: int
    one_min_timestamp = 60_000
    time_identifier = timeframe[-1]
    time_multiplier = int(timeframe.replace(time_identifier, ''))
    return int(time_dict[time_identifier] * one_min_timestamp * time_multiplier)


@cache
def get_all_markets() -> list[str]:
    client = Client()
    all_symbols_ticker = client.get_all_tickers()
    all_symbols = []
    for data in all_symbols_ticker:
        if "USDT" == data['symbol'][-4:]:
            all_symbols.append(data['symbol'])
    client.close_connection()
    return all_symbols
