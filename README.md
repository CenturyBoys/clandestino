# Clandestino

![banner](docs/banner.jpeg)

```
By: CenturyBoys
```

This package provides a migration tool. It includes a command-line interface (CLI) for easy execution and a single asynchronous function that can be imported and used in your code.

## Install

The main package does not have any database implementation and uses only the interfaces and abstractions from the `clandestino_interfaces` package. In other words, you are free to create your own implementations. We will explain the details later.

| Database Type | Install using extra | description                             | Environment parameter                       |
|---------------|---------------------|-----------------------------------------|---------------------------------------------|
| PostgreSQL    | postgres            | [here](extras/postgres/README.md)       | CLANDESTINO_POSTGRES_CONNECTION_STRING      |
| Elasticsearch | elasticsearch       | [here](extras/elasticsearch/README.md)  | CLANDESTINO_ELASTICSEARCH_CONNECTION_STRING |
| MongoDB       | mongo               | [here](extras/mongo/README.md)          | CLANDESTINO_MONGO_CONNECTION_STRING         |

How to install extra packages?

```shell
poetry add clandestino -E postgres
OR
pip install 'romeways[postgres]'
```

## Config

Clandestino has some configurations that you can set as environment variables or in a `.env` file.

- `CLANDESTINO_MIGRATION_REPO` If you are using any of the extra packages, you must set them with their respective values: `POSTGRES`, `ELASTICSEARCH`, `MONGO`

## CLI

### [-h] Help command

```bash
$cdt -h         
 Clandestino is a database migration tool
 Migration repository mode is: ELASTICSEARCH
  cldest [-h|-m|-lm|-rm|-cm] [params]

    -h: Display help
    -m: Migrate database
    -lm: List migrations
    -rm: Rollback last migration
    -cm: Create database migration - params [name type]
```

### [-m] Migrate database

Migrate databases using the files within the `./migrations` folder. Each migration checks if it's already run. If not, the migration is applied, the information is saved, and the async def up(self) -> None method is called. No migration will be executed twice.

The system will display the migration status:
- OK = ✅
- ERROR = ⚠️
- SKIPPED = ⏭️

### [-lm] List migrations

List all migration within the `./migrations` folder

### [-rm] Rollback migration

Rollback the last database migration using the latest file in the `./migrations` folder. The `async def down(self) -> None` method within the file will be called.

The system will display the rollback status:
- OK = ✅
- ERROR = ⚠️
- SKIPPED = ⏭️

### [-cm] Create migration

Create a migration within the `./migrations` folder, if the folder not exists create it to. 

This command receive two parameters:

- Migration name 
- Migration type, if not filled will use default migration template.

The migration file will be like this `migration_{datetime_reference}_{migration_name}.py`

## Migration file

The migration file inherit the abstract class `AbstractMigration` and need declare two fundtions:

- `async def up(self) -> None`. This method will be called on migration command
- `async def down(self) -> None`. This method will be called on rollback command

See bellow an empty template file

```python
from clandestino_interfaces import AbstractMigration

class Migration(AbstractMigration):

    infra = None

    async def up(self) -> None:
        """Do modifications in database"""
        pass

    async def down(self) -> None:
        """Undo modifications in database"""
        pass
```

## Self Implementation

To create your own Clandestino implementation, simply create a file named `repository.py` inside the `./migrations` folder. This file should contain a class named `MigrateRepository` that inherits from `clandestino_interfaces.IMigrateRepository`.

Observation: Your migrations need to handler the database connections by your self.

See bellow the interface:

```python
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
```