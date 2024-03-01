from contextlib import asynccontextmanager

from decouple import config
from elasticsearch import AsyncElasticsearch


class ElasticsearchInfra:
    __client = None

    @classmethod
    def __get_client(cls) -> AsyncElasticsearch:
        if cls.__client is None:
            str_connection = config("CLANDESTINO_ELASTICSEARCH_CONNECTION_STRING")
            cls.__client = AsyncElasticsearch(str_connection, verify_certs=False)
        return cls.__client

    @classmethod
    async def __close_client(cls) -> None:
        if cls.__client is not None:
            await cls.__client.close()
            cls.__client = None

    @classmethod
    @asynccontextmanager
    async def get_client(cls) -> AsyncElasticsearch:
        async_client = None
        try:
            async_client = cls.__get_client()
            yield async_client
        except Exception as e:
            print(f"{cls.__class__}::get_client")
            raise e
        finally:
            if async_client:
                await cls.__close_client()
