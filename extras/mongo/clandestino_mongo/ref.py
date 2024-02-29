from clandestino_interfaces import AbstractMigration
from clandestino_mongo.infra import MongoInfra


class Migration(AbstractMigration):

    infra = MongoInfra()

    async def up(self) -> None:
        """Do modifications in database"""
        pass

    async def down(self) -> None:
        """Undo modifications in database"""
        pass
