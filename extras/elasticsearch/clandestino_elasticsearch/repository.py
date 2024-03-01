import datetime

from elasticsearch import NotFoundError

from .infra import ElasticsearchInfra

from clandestino_interfaces import IMigrateRepository


class ElasticsearchMigrateRepository(IMigrateRepository, ElasticsearchInfra):

    @classmethod
    def get_control_index(cls):
        return "clandestino"

    @classmethod
    async def create_control_table(cls) -> None:
        async with cls.get_client() as es_client:
            await es_client.index(
                index=cls.get_control_index(),
                id="init",
                document={"name": "clandestino init"},
            )

    @classmethod
    async def control_table_exists(cls) -> bool:
        async with cls.get_client() as es_client:
            result = await es_client.indices.exists(index=cls.get_control_index())
            return bool(result)

    @classmethod
    async def register_migration_execution(cls, migration_name: str) -> None:
        async with cls.get_client() as es_client:
            await es_client.index(
                index=cls.get_control_index(),
                id=migration_name,
                document={
                    "name": migration_name,
                    "created_at": str(datetime.datetime.utcnow()),
                },
            )

    @classmethod
    async def remove_migration_execution(cls, migration_name: str) -> None:
        async with cls.get_client() as es_client:
            await es_client.delete(
                index=cls.get_control_index(),
                id=migration_name,
            )

    @classmethod
    async def migration_already_executed(cls, migration_name: str) -> bool:
        async with cls.get_client() as es_client:
            try:
                result = await es_client.get(
                    index=cls.get_control_index(),
                    id=migration_name,
                )
                return bool(result)
            except NotFoundError as e:
                return False
