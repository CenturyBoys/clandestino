from clandestino_interfaces import AbstractMigration
from clandestino_postgres.infra import PostgresInfra


class Migration(AbstractMigration):

    infra = PostgresInfra()

    async def up(self) -> None:
        """Do modifications in database"""
        sql = f"""
            CREATE TABLE A1 (
                company_cnpj VARCHAR (18) NOT NULL PRIMARY KEY,
                version INT NOT NULL
            );
        """
        async with self.infra.get_cursor() as cursor:
            await cursor.execute(sql)

    async def down(self) -> None:
        """Undo modifications in database"""
        sql = f"""
            DROP TABLE A1;
        """
        async with self.infra.get_cursor() as cursor:
            await cursor.execute(sql)
