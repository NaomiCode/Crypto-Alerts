from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import atexit

client = MongoClient("localhost", 27017, maxPoolSize=None)


def duplicate_key_handler(func):
    def wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except DuplicateKeyError:
            return False

    return wrap


def close_database():
    client.close()


atexit.register(close_database)
