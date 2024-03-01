from clandestino_interfaces import AbstractMigration
from clandestino_elasticsearch.infra import ElasticsearchInfra


class Migration(AbstractMigration):

    infra = ElasticsearchInfra()

    async def up(self) -> None:
        """Do modifications in database"""
        pass

    async def down(self) -> None:
        """Undo modifications in database"""
        pass
