from clandestino_interfaces import AbstractMigration


class Migration(AbstractMigration):

    infra = None

    async def up(self) -> None:
        """Do modifications in database"""
        pass

    async def down(self) -> None:
        """Undo modifications in database"""
        pass
