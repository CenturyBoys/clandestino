from abc import ABC, abstractmethod

from .enum import MigrationStatus
from .interface import IMigrateRepository


class AbstractMigration(ABC):
    def __init__(self, migration_name: str, migration_repository: IMigrateRepository):
        self._name = migration_name
        self._repo = migration_repository

    @abstractmethod
    async def up(self) -> None:
        """Do modifications in database"""
        pass

    @abstractmethod
    async def down(self) -> None:
        """Undo modifications in database"""
        pass

    async def __down(self) -> None:
        try:
            await self.down()
        except BaseException as e:
            print(e)

    async def __must_run_this_migration(self) -> bool:
        control_table_exists = await self._repo.control_table_exists()
        if not control_table_exists:
            await self._repo.create_control_table()
        migration_already_executed = await self._repo.migration_already_executed(
            migration_name=self._name
        )
        return not migration_already_executed

    async def __save_execution(self) -> None:
        await self._repo.register_migration_execution(migration_name=self._name)

    async def __remove_execution(self) -> None:
        await self._repo.remove_migration_execution(migration_name=self._name)

    async def roll_back_migration(self) -> None:
        print(f"-> rolling back {self._name}", end="")
        must_run_this_migration = await self.__must_run_this_migration()
        if not must_run_this_migration:
            try:
                await self.__down()
                await self.__remove_execution()
                print(f" {MigrationStatus.OK.value}")
            except BaseException as e:
                print(f" {MigrationStatus.ERROR.value}")
                raise e
        else:
            print(f" {MigrationStatus.SKIPPED.value}")

    async def migrate(self) -> None:
        print(f"-> running {self._name}", end="")
        must_run_this_migration = await self.__must_run_this_migration()
        if must_run_this_migration:
            try:
                await self.up()
                await self.__save_execution()
                print(f" {MigrationStatus.OK.value}")
            except BaseException as e:
                await self.__down()
                print(f" {MigrationStatus.ERROR.value}")
                raise e
        else:
            print(f" {MigrationStatus.SKIPPED.value}")
