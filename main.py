import multiprocessing
import os
import time
from binance import ThreadedWebsocketManager, Client
from dotenv import load_dotenv
from binance_data.main import timeframe_to_timestamp_milliseconds
from bot import start_bot
from dispatcher.dispatcher import websocket_handler
from project_types.types import MonitorSymbols, Kline
from database.operation import add_monitor_to_queue, number_of_entries_kline, insert_kline

load_dotenv()


def kline_format(data: list, symbol: str, time_frame: str):
    data.pop()
    for datum in data:
        kline = Kline(_id=datum[0],
                      symbol=symbol, time_frame=time_frame, open=float(datum[1]), close=float(datum[4]),
                      high=float(datum[2]), low=float(datum[3]), volume=float(datum[5]))
        insert_kline(kline)


def twm(data: multiprocessing.Queue):
    while True:
        try:
            sym_tf: set[tuple[str, str]] = data.get()
            tw = ThreadedWebsocketManager()
            tw.start()
            while True:
                if list(sym_tf):
                    for sym, tf in list(sym_tf):
                        entries_count, last_entry = number_of_entries_kline(sym, tf)
                        if entries_count < 100:
                            client_bs = Client()
                            kline_format(client_bs.get_historical_klines(sym, tf), sym, tf)
                            client_bs.close_connection()
                        elif last_entry['_id'] > time.time() * 1000 - timeframe_to_timestamp_milliseconds(tf):
                            client_bs = Client()
                            kline_format(client_bs.get_historical_klines(sym, tf), sym, tf)
                            client_bs.close_connection()
                        tw.start_kline_socket(symbol=sym, interval=tf, callback=websocket_handler)
                while True:
                    sym_tf_ = data.get()
                    if sym_tf_ != sym_tf:
                        sym_tf = sym_tf_
                        break
                tw.stop()
                tw.join()
                tw = ThreadedWebsocketManager()
                tw.start()
        except Exception as e:
            print(e)


def monitor_worker(worker_queue: multiprocessing.Queue, outbound_queue: multiprocessing.Queue):
    monitor_set = set()
    while True:
        obj: MonitorSymbols = worker_queue.get()
        data = obj.get_monitor()
        if data[3]:
            monitor_set.add((data[0], data[1]))
        else:
            monitor_set.remove((data[0], data[1]))
        outbound_queue.put(monitor_set)


if __name__ == '__main__':
    main_queue = multiprocessing.Queue()
    monitor_worker_outbound_queue = multiprocessing.Queue()
    add_monitor_to_queue(main_queue)
    candle_stick_data_queue = multiprocessing.Queue()
    telegram = multiprocessing.Process(target=start_bot, args=(os.getenv("TELEGRAM_BOT_TOKEN"), main_queue))
    monitor = multiprocessing.Process(target=monitor_worker, args=(main_queue, monitor_worker_outbound_queue))
    data_handler = multiprocessing.Process(target=twm, args=(monitor_worker_outbound_queue,))
    telegram.start()
    monitor.start()
    data_handler.start()
    telegram.join()
    monitor.join()
    data_handler.join()
