from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import mongoengine

from config import MONGO_URI, DB_NAME


def get_pymongo_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_pymongo_db():
    return get_pymongo_client()[DB_NAME]


def get_motor_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(MONGO_URI)


def get_motor_db():
    return get_motor_client()[DB_NAME]


def connect_mongoengine():
    mongoengine.connect(DB_NAME, host=MONGO_URI)


def disconnect_mongoengine():
    mongoengine.disconnect()
