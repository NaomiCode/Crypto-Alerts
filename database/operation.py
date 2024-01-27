import multiprocessing
from database.client import duplicate_key_handler, client
from project_types.types import Tick, Kline, Strategy, User, KlineFind, MonitorSymbols
from pymongo.errors import DuplicateKeyError


def insert_kline(data: Kline):
    db = client[data['symbol'] + "-kline"]
    col = db[data['time_frame']]
    data.pop("time_frame")
    data.pop("symbol")
    try:
        col.insert_one(data)
    except DuplicateKeyError:
        col.replace_one({'_id': data['_id']}, data, upsert=True)


def insert_klines(data: list[Kline]):
    db = client[data[0]['symbol'] + "-kline"]
    col = db[data[0]['time_frame']]
    for datum in data:
        try:
            datum.pop("time_frame")
            datum.pop("symbol")
            col.insert_one(datum)
        except DuplicateKeyError:
            col.replace_one({'_id': datum['_id']}, datum, upsert=True)


@duplicate_key_handler
def insert_ticker(data: Tick):
    db = client['Tick']
    col = db[data['symbol']]
    data.pop("symbol")
    col.insert_one(data)


@duplicate_key_handler
def insert_user(data: User):
    db = client['users']
    col = db[data['user_type']]
    n_data = data.copy()
    n_data.pop("user_type")
    col.insert_one(n_data)


@duplicate_key_handler
def insert_user_strategy(data: Strategy):
    db = client['strategies']
    col = db[data['name']]
    data.pop("name")
    for item in data['users_id']:
        res = col.find_one_and_update({"symbol": data['symbol'], 'time_frame': data['time_frame']},
                                      {'$addToSet': {"users_id": item}})
        if res is None:
            col.insert_one(data)


@duplicate_key_handler
def delete_user_strategy(data: Strategy):
    db = client['strategies']
    col = db[data['name']]
    data.pop("name")
    for item in data['users_id']:
        res = col.find_one_and_update({"symbol": data['symbol'], 'time_frame': data['time_frame']},
                                      {'$pull': {"users_id": item}})
        if res is None:
            col.insert_one(data)


def find_last_kline(data: KlineFind):
    db = client[data['symbol'] + "-kline"]
    col = db[data['time_frame']]
    result = col.find().sort('_id', -1).limit(data['quantity'])
    return result


def find_all_klines(data: KlineFind):
    db = client[data['symbol'] + "-kline"]
    col = db[data['time_frame']]
    result = col.find().sort('_id')
    return result


def find_strategy_users_id(name: str, time_frame: str, symbol: str) -> list | None:
    db = client['strategies']
    col = db[name]
    for item in col.find():
        if item['symbol'] == symbol and item['time_frame'] == time_frame:
            return item['users_id']
    return None


def find_monitor_symbols() -> dict[str:list]:
    db = client['strategies']
    cols = db.list_collection_names()
    results = {}
    for collection in cols:
        results = {}
        col = db[collection]
        for item in col.find({}):
            if item['users_id']:
                if item['time_frame'] in results.keys():
                    results[item['time_frame']].append(item['symbol'])
                else:
                    results[item['time_frame']] = [item['symbol']]

    return results


def add_monitor_to_queue(q: multiprocessing.Queue):
    db = client['strategies']
    cols = db.list_collection_names()
    for collection in cols:
        col = db[collection]
        for item in col.find({}):
            if item['users_id']:
                q.put(MonitorSymbols(item['symbol'], item['time_frame'], collection, True))


def number_of_entries_kline(symbol: str, time_frame: str):
    db = client[symbol + "-kline"]
    col = db[time_frame]
    entries = col.find({})
    if len(list(entries)) == 0:
        return 0, 0
    else:
        return len(list(col.find({}))), col.find({}).sort('_id', -1).limit(1)[0]
