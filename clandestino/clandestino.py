import os
import sys
import asyncio
from datetime import datetime
from decouple import AutoConfig
from importlib import import_module
from pkgutil import iter_modules

import clandestino_interfaces as cdti

config = AutoConfig(search_path=f"{os.getcwd()}")

_cdtp = None
_cdtm = None
_cdte = None

OPTION_STARTSWITH = "-"

available_options = {
    "-h": {
        "description": "Display help",
        "params": [],
    },
    "-m": {
        "description": "Migrate database",
        "params": [],
    },
    "-lm": {
        "description": "List migrations",
        "params": [],
    },
    "-rm": {
        "description": "Rollback last migration",
        "params": [],
    },
    "-cm": {
        "description": "Create database migration",
        "params": ["name", "type"],
    },
}


def print_sep():
    print("=" * 100)


async def help_callback():

    clandestino_options = f"cldest [{'|'.join(available_options.keys())}] [params]"
    header = (
        """ Clandestino is a database migration tool\n"""
        f""" Migration repository mode is: {config('CLANDESTINO_MIGRATION_REPO')}\n"""
        f"  {clandestino_options}\n"
    )
    print(header)
    for available_option, metadata in available_options.items():
        _option = available_option
        _option_description = metadata["description"]
        _option_params = metadata["params"]
        options_str = f"    {_option}: {_option_description}"
        if _option_params:
            options_str += f" - params [{' '.join(_option_params)}]"
        print(options_str)
    print("\n")


def _load_migration_repository() -> cdti.IMigrateRepository:
    self_implemented_repository = (
        f"{os.getcwd()}{os.sep}migrations{os.sep}repository.py"
    )
    if os.path.exists(self_implemented_repository):
        my_repository = import_module(self_implemented_repository)
        return my_repository.MigrateRepository()

    elif config("CLANDESTINO_MIGRATION_REPO", default=False) == "POSTGRES":
        return _cdtp.repository.PostgresMigrateRepository()
    elif config("CLANDESTINO_MIGRATION_REPO", default=False) == "MONGO":
        return _cdtm.repository.MongoMigrateRepository()
    elif config("CLANDESTINO_MIGRATION_REPO", default=False) == "ELASTICSEARCH":
        return _cdte.repository.ElasticsearchMigrateRepository()


async def migrate_database():
    load()
    print(
        "Running migrations: " f"{cdti.MigrationStatus.OK.value} - success | ",
        f"{cdti.MigrationStatus.ERROR.value} - error | ",
        f"{cdti.MigrationStatus.SKIPPED.value} - skipped",
    )
    print_sep()
    _path = f"{os.getcwd()}{os.sep}migrations"
    sys.path.append(_path)
    for importer, migration_name, is_package in iter_modules([_path]):
        if str(migration_name).startswith("migration"):
            if not is_package:
                migration_import_reference = import_module(migration_name)
                migration: cdti.AbstractMigration = (
                    migration_import_reference.Migration(
                        migration_name=migration_name,
                        migration_repository=_load_migration_repository(),
                    )
                )
                await migration.migrate()


async def list_migrate_database():
    print("Migrations: ")
    print_sep()
    for _, migration_name, _ in iter_modules([f"{os.getcwd()}{os.sep}migrations"]):
        if str(migration_name).startswith("migration"):
            print(migration_name)


async def rollback_migration():
    modules_list = [
        (importer, migration_name, is_package)
        for importer, migration_name, is_package in iter_modules(
            [f"{os.getcwd()}{os.sep}migrations"]
        )
    ]
    if modules_list:
        last_migration = modules_list[-1]
        importer, migration_name, is_package = last_migration
        if not is_package:
            answer = input(
                f"You relly want to roll back this migration '{migration_name}'? Y/n: "
            )
            if answer == "Y":
                print(
                    "Roll back migrations: "
                    f"{cdti.MigrationStatus.OK.value} - success | ",
                    f"{cdti.MigrationStatus.ERROR.value} - error | ",
                    f"{cdti.MigrationStatus.SKIPPED.value} - skipped",
                )
                print_sep()

                import_str = f"migrations.{migration_name}"
                migration_import_reference = import_module(import_str)
                migration: cdti.AbstractMigration = (
                    migration_import_reference.Migration(
                        migration_name=migration_name,
                        migration_repository=_load_migration_repository(),
                    )
                )
                await migration.roll_back_migration()


def _migration_name(migration_name: str) -> str:
    datetime_reference = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"migration_{datetime_reference}_{migration_name}.py"
    return file_name


def _get_path() -> str:
    path = f"{os.getcwd()}{os.sep}migrations"
    if not os.path.exists(path):
        print(f"Path not exists: {path}, creating!")
        os.mkdir(path)
    return path


def _get_ref_migration(migration_type: str = None) -> str:
    if migration_type is not None:
        migration_type = migration_type.upper()
    self_implemented_repository = f"{os.getcwd()}{os.sep}migrations{os.sep}ref.py"
    if os.path.exists(self_implemented_repository):
        return self_implemented_repository
    elif migration_type == "POSTGRES":
        return _cdtp.ref.__file__
    elif migration_type == "MONGO":
        return _cdtm.ref.__file__
    elif migration_type == "ELASTICSEARCH":
        return _cdte.ref.__file__
    else:
        from .src import ref

        return ref.__file__


async def create_database_migrate(migration_name: str, migration_type: str = None):
    path = _get_path()
    file_name = _migration_name(migration_name)
    print(
        f"Creating {migration_type if migration_type else 'empty'} migration: {file_name} ",
        end="",
    )
    try:
        with open(f"{path}{os.sep}{file_name}", "w") as migration_file:
            with open(_get_ref_migration(migration_type), "r") as migration_ref_file:
                migration_file.write(migration_ref_file.read())
        print(cdti.MigrationStatus.OK.value)
    except BaseException as e:
        print(cdti.MigrationStatus.ERROR.value)
        raise e


options_callback = {
    "-h": help_callback,
    "-m": migrate_database,
    "-lm": list_migrate_database,
    "-rm": rollback_migration,
    "-cm": create_database_migrate,
}



def load():
    global _loaded
    if not _loaded:
        try:
            import clandestino_postgres

            global _cdtp
            _cdtp = clandestino_postgres
        except ImportError as error:
            if config("CLANDESTINO_MIGRATION_REPO", default=False) == "POSTGRES":
                raise Exception(
                    "You define to use POSTGRES but not install the extra package clandestino_postgres"
                )

        try:
            import clandestino_mongo

            global _cdtm
            _cdtm = clandestino_mongo
        except ImportError as error:
            if config("CLANDESTINO_MIGRATION_REPO", default=False) == "MONGO":
                raise Exception(
                    "You define to use MONGO but not install the extra package clandestino_mongo"
                )

        try:
            import clandestino_elasticsearch

            global _cdte
            _cdte = clandestino_elasticsearch
        except ImportError as error:
            if config("CLANDESTINO_MIGRATION_REPO", default=False) == "ELASTICSEARCH":
                raise Exception(
                    "You define to use MONGO but not install the extra package clandestino_elasticsearch"
                )
    _loaded = True

def main():
    load()
    raw_inputs_param = sys.argv[1:]
    is_valid_option = False
    if raw_inputs_param:
        inputs_param = raw_inputs_param.copy()
        option = inputs_param.pop(0)
        if command_metadata := available_options.get(option):
            option_params = command_metadata["params"]
            is_valid_option = option.startswith(OPTION_STARTSWITH) and len(
                option_params
            ) == len(inputs_param)
        if is_valid_option:
            callback = options_callback[option]
            asyncio.run(callback(*inputs_param))

    if not raw_inputs_param or not is_valid_option:
        asyncio.run(help_callback())
