import os

from contextlib import asynccontextmanager

from decouple import AutoConfig
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

config = AutoConfig(search_path=os.getcwd())


class MongoInfra:
    __client = None

    @classmethod
    def __get_client(cls) -> AsyncIOMotorClient:
        if cls.__client is None:
            str_connection = config("CLANDESTINO_MONGO_CONNECTION_STRING")
            cls.__client = AsyncIOMotorClient(str_connection)
        return cls.__client

    @classmethod
    async def __close_client(cls) -> AsyncIOMotorClient:
        if cls.__client is not None:
            cls.__client.close()
            cls.__client = None

    @classmethod
    @asynccontextmanager
    async def get_database(cls) -> AsyncIOMotorDatabase:
        async_client = None
        try:
            async_client = cls.__get_client()
            yield async_client.get_default_database()
        except Exception as e:
            print(f"{cls.__class__}::get_client")
            raise e
        finally:
            if async_client:
                await cls.__close_client()
