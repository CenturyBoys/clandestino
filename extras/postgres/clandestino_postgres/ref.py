from clandestino_interfaces import AbstractMigration
from clandestino_postgres.infra import PostgresInfra


class Migration(AbstractMigration):

    infra = PostgresInfra()

    async def up(self) -> None:
        """Do modifications in database"""
        pass

    async def down(self) -> None:
        """Undo modifications in database"""
        pass
