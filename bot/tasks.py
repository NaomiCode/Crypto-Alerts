import multiprocessing
from binance_data.main import get_all_markets
from database.client import client
from database.operation import insert_user_strategy, delete_user_strategy
from project_types.types import Strategy, MonitorSymbols

strategies = ["fibo", "sharp"]
tf = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']


def reset_handler(arguments: list[str], user_id: int, q: multiprocessing.Queue) -> str:
    if len(arguments) == 1:
        if arguments[0] == "all":
            if reset_all(user_id, q):
                return "✅ all settings have been rested successfully"
            else:
                return "Error!"
        elif arguments[0].upper() in get_all_markets():
            if reset_symbol(user_id, arguments[0].upper(), q):
                return f"✅ all settings on {arguments[0].upper()} have been reset successfully"
            else:
                return "❌ Error!"
        else:
            return f"❌ {arguments[0].upper()} is not a valid symbol"
    elif len(arguments) > 1:
        return f"❌ too many arguments!\n only one argument is allowed"
    else:
        return "❌ specify one argument to reset"


def reset_all(user_id: int, q: multiprocessing.Queue):
    try:
        db = client['strategies']
        collections = db.list_collection_names()
        for collection in collections:
            col = db[collection]
            for item in col.find():
                if user_id in item['users_id']:
                    if len(item['users_id']) > 1:
                        col.find_one_and_update({'_id': item['_id']}, {'$pull': {'users_id': user_id}})
                    else:
                        document = col.find_one({'_id': item['_id']})
                        q.put(MonitorSymbols(document['symbol'], document['time_frame'], collection, False))
                        col.find_one_and_delete({'_id': item['_id']})
        return True
    except Exception as e:
        print(e)
        return False


def reset_symbol(user_id: int, symbol: str, q: multiprocessing.Queue):
    try:
        db = client['strategies']
        collections = db.list_collection_names()
        for collection in collections:
            col = db[collection]
            for item in col.find():
                if user_id in item['users_id'] and symbol == item['symbol']:
                    if len(item['users_id']) > 1:
                        col.find_one_and_update({'_id': item['_id']}, {'$pull': {'users_id': user_id}})
                    else:
                        document = col.find_one({'_id': item['_id']})
                        q.put(MonitorSymbols(document['symbol'], document['time_frame'], collection, False))
                        col.find_one_and_delete({'_id': item['_id']})
        return True
    except:
        return False


def status_handler(arguments: list[str], user_id: int) -> str:
    if len(arguments) > 1 or len(arguments) == 0:
        return "❌ specify only one argument to reset"
    else:
        if arguments[0] == "all":
            return status_all(user_id)
        elif arguments[0].upper() in get_all_markets():
            return status_symbol(user_id, arguments[0].upper())
        else:
            return f"❌ {arguments[0].upper()} is not a valid symbol"


def status_all(user_id: int) -> str:
    try:
        db = client['strategies']
        collections = db.list_collection_names()
        result = ""
        for collection in collections:
            col = db[collection]
            for item in col.find():
                if user_id in item['users_id']:
                    result += f"\n✅ {collection} {item['symbol']} {item['time_frame']} "

        if result != "":
            return result
        else:
            return "no entries found"
    except:
        return "❌ Error!"


def status_symbol(user_id: int, symbol: str) -> str:
    try:
        db = client['strategies']
        collections = db.list_collection_names()
        result = ""
        for collection in collections:
            col = db[collection]
            for item in col.find():
                if user_id in item['users_id'] and item['symbol'] == symbol.upper():
                    result += f"\n✅ {collection} {item['symbol']} {item['time_frame']} "
        if result != "":
            return result
        else:
            return "no entries found"
    except:
        return "❌ no entries yet"


def start_handler(arguments: list[str], user_id: int, queue: multiprocessing.Queue) -> str:
    if arguments[0].upper() in get_all_markets():
        if arguments[1].lower() in tf:
            if arguments[2].lower() in strategies:
                insert_user_strategy(
                    Strategy(name=arguments[2].lower(), time_frame=arguments[1].lower(), symbol=arguments[0].upper(),
                             users_id=[user_id]))
                queue.put(MonitorSymbols(arguments[0].upper(), arguments[1].lower(), arguments[2].lower(), True))
                return f"✅successfully started strategy {arguments[2]} for {arguments[0]} in {arguments[1]} timeframe"
            else:
                return f"❌ {arguments[2].lower()} is not a valid strategy"
        else:
            return f"❌ {arguments[1].lower()} is not a valid timeframe"
    else:
        return f"❌ {arguments[0].upper()} is not a valid symbol"


def stop_handler(arguments: list[str], user_id: int, queue: multiprocessing.Queue):
    if arguments[0].upper() in get_all_markets():
        if arguments[1].lower() in tf:
            if arguments[2].lower() in strategies:
                delete_user_strategy(
                    Strategy(name=arguments[2].lower(), time_frame=arguments[1].lower(), symbol=arguments[0].upper(),
                             users_id=[user_id]))
                queue.put(MonitorSymbols(arguments[0].upper(), arguments[1].lower(), arguments[2].lower(), False))
                return f"✅successfully stopped strategy {arguments[2]} for {arguments[0]} in {arguments[1]} timeframe"
            else:
                return f"❌ {arguments[2].lower()} is not a valid strategy"
        else:
            return f"❌ {arguments[1].lower()} is not a valid timeframe"
    else:
        return f"❌ {arguments[0].upper()} is not a valid symbol"
