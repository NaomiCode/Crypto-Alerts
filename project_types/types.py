from typing import TypedDict
from typing_extensions import Required, NotRequired
from datetime import datetime


class MonitorSymbols(object):
    def __init__(self, symbol:str, timeframe:str, strategy:str, enabled:bool):
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy = strategy
        self.enabled = enabled

    def get_monitor(self)->tuple:
        return self.symbol, self.timeframe, self.strategy, self.enabled

class Tick(TypedDict):
    symbol: NotRequired[str]
    time_frame: NotRequired[str]
    _id: Required[datetime]
    open_time: Required[datetime]
    close_time: Required[datetime]
    open: Required[float]
    close: Required[float]
    high: Required[float]
    low: Required[float]
    volume: Required[float]


class Kline(TypedDict):
    symbol: NotRequired[str]
    time_frame: NotRequired[str]
    _id: Required[datetime]
    open: Required[float]
    close: Required[float]
    high: Required[float]
    low: Required[float]
    volume: Required[float]


class KlineFind(TypedDict):
    symbol: Required[str]
    time_frame: Required[str]
    quantity: NotRequired[int]


class Strategy(TypedDict):
    name: NotRequired[str]
    symbol: Required[str]
    time_frame: Required[str]
    users_id: NotRequired[list[int]]


class User(TypedDict):
    user_type: Required[str]
    name: Required[str]
    user_id: NotRequired[int]
    username: Required[str]