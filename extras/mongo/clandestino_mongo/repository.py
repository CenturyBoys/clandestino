import datetime

from clandestino_mongo import MongoInfra

from clandestino_interfaces import IMigrateRepository


class MongoMigrateRepository(IMigrateRepository, MongoInfra):

    @classmethod
    def get_control_collection(cls):
        return "clandestino"

    @classmethod
    async def create_control_table(cls) -> None:
        control_collection = cls.get_control_collection()
        query = {"name": "clandestino init"}
        async with cls.get_database() as database:
            collection = database[control_collection]
            await collection.insert_one(query)

    @classmethod
    async def control_table_exists(cls) -> bool:
        control_collection = cls.get_control_collection()
        async with cls.get_database() as database:
            collections = await database.list_collection_names()
            return control_collection in collections

    @classmethod
    async def register_migration_execution(cls, migration_name: str) -> None:
        control_collection = cls.get_control_collection()
        query = {
            "name": migration_name,
            "created_at": datetime.datetime.utcnow()
        }
        async with cls.get_database() as database:
            collection = database[control_collection]
            await collection.insert_one(query)

    @classmethod
    async def remove_migration_execution(cls, migration_name: str) -> None:
        control_collection = cls.get_control_collection()
        query = {
            "name": migration_name
        }
        async with cls.get_database() as database:
            collection = database[control_collection]
            await collection.delete_one(query)

    @classmethod
    async def migration_already_executed(cls, migration_name: str) -> bool:
        control_collection = cls.get_control_collection()
        query = {
            "name": migration_name
        }
        async with cls.get_database() as database:
            collection = database[control_collection]
            result = await collection.find_one(query)
            return bool(result)
