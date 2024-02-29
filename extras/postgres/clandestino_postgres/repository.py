from clandestino_postgres import PostgresInfra

from clandestino_interfaces import IMigrateRepository


class PostgresMigrateRepository(IMigrateRepository, PostgresInfra):

    @classmethod
    def get_control_table(cls):
        return "clandestino"

    @classmethod
    async def create_control_table(cls) -> None:
        control_table = cls.get_control_table()
        sql = f"""
            CREATE TABLE {control_table}(
                id serial PRIMARY KEY,
                migration_name VARCHAR ( 255 ) UNIQUE NOT NULL,
                created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        async with cls.get_cursor() as cursor:
            await cursor.execute(sql)

    @classmethod
    async def control_table_exists(cls) -> bool:
        control_table = cls.get_control_table()
        sql = f"""
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE tablename = %s
            );
        """
        async with cls.get_cursor() as cursor:
            await cursor.execute(sql, [control_table])
            result = await cursor.fetchone()
        return bool(result[0])

    @classmethod
    async def register_migration_execution(cls, migration_name: str) -> None:
        control_table = cls.get_control_table()
        sql = f"""
            INSERT INTO {control_table}(migration_name)
            VALUES (%s);
        """
        async with cls.get_cursor() as cursor:
            await cursor.execute(sql, [migration_name])

    @classmethod
    async def remove_migration_execution(cls, migration_name: str) -> None:
        control_table = cls.get_control_table()
        sql = f"""
            DELETE FROM {control_table} WHERE migration_name = %s;
        """
        async with cls.get_cursor() as cursor:
            await cursor.execute(sql, [migration_name])

    @classmethod
    async def migration_already_executed(cls, migration_name: str) -> bool:
        control_table = cls.get_control_table()
        sql = f"""
            SELECT EXISTS (
                SELECT FROM {control_table}
                WHERE migration_name = %s
            );
        """
        async with cls.get_cursor() as cursor:
            await cursor.execute(sql, [migration_name])
            result = await cursor.fetchone()
        return bool(result[0])
