import os

from contextlib import asynccontextmanager

from decouple import AutoConfig
from psycopg import AsyncConnection, AsyncCursor

config = AutoConfig(search_path=os.getcwd())


class PostgresInfra:
    __connection = None

    @classmethod
    async def __get_connection(cls) -> AsyncConnection:
        if cls.__connection is None:
            str_connection = config("CLANDESTINO_POSTGRES_CONNECTION_STRING")
            cls.__connection = await AsyncConnection.connect(str_connection)
        return cls.__connection

    @classmethod
    @asynccontextmanager
    async def get_cursor(cls) -> AsyncCursor:
        async_connection = None
        try:
            async_connection = await cls.__get_connection()
            async with async_connection.cursor() as cursor:
                yield cursor
        except Exception as e:
            print(f"{cls.__class__}::get_cursor")
            raise e
        finally:
            if async_connection:
                await async_connection.commit()
