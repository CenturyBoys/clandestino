from abc import ABC, abstractmethod


class IMigrateRepository(ABC):
    @classmethod
    @abstractmethod
    async def create_control_table(cls) -> None:
        pass

    @classmethod
    @abstractmethod
    async def control_table_exists(cls) -> bool:
        pass

    @classmethod
    @abstractmethod
    async def register_migration_execution(cls, migration_name: str) -> None:
        pass

    @classmethod
    @abstractmethod
    async def migration_already_executed(cls, migration_name: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    async def remove_migration_execution(cls, migration_name: str) -> None:
        pass
