from clandestino_interfaces import AbstractMigration
from clandestino_mongo.infra import MongoInfra


class Migration(AbstractMigration):

    infra = MongoInfra()

    async def up(self) -> None:
        """Do modifications in database"""
        query = {"name": "Test"}
        async with self.infra.get_database() as database:
            collection = database["test"]
            await collection.insert_one(query)

    async def down(self) -> None:
        """Undo modifications in database"""
        query = {
            "name": "Test"
        }
        async with self.infra.get_database() as database:
            collection = database["test"]
            await collection.delete_one(query)
