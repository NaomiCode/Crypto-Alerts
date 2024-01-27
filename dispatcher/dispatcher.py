import datetime
import pytz
from database.operation import insert_kline, insert_ticker
from logic.fibo import fibo_retracement
from logic.sharp import sharp_finder
from project_types.types import Kline, Tick

def ticker_format(message: dict) -> Tick:
    candle = message['k']
    return Tick(_id=datetime.datetime.fromtimestamp(float(message['E']) / 1000, pytz.UTC),
                open_time=datetime.datetime.fromtimestamp(float(candle['t']) / 1000, pytz.UTC),
                close_time=datetime.datetime.fromtimestamp(float(candle['T']) / 1000, pytz.UTC),
                open=float(candle['o']), high=float(candle['h']), symbol=message['s'],
                low=float(candle['l']), close=float(candle['c']), volume=float(candle['v'], ))


def kline_handler(res):
    insert_kline(tick_to_kline(res))


def ticker_handler(res):
    insert_ticker(ticker_format(res))


def tick_to_kline(data: dict) -> Kline:
    return Kline(symbol=data['s'], time_frame=data['k']["i"], _id=data['k']["t"], open=float(data['k']["o"]),
                 high=float(data['k']["h"]), low=float(data['k']["l"]), close=float(data['k']["c"]),
                 volume=float(data['k']["v"]))


def websocket_handler(res):
    if "k" in res.keys():
        if res['k']['x'] is True:
            kline_handler(res)
            sharp_finder(res['s'], res['k']['i'],3)
            fibo_retracement(res['s'], res['k']['i'], 10)
        if res['k']['i'] == '1m' and res['k']['x'] is False:
            ticker_handler(res)
