from enum import Enum


class MigrationStatus(Enum):
    OK = "✔"
    ERROR = "⚠"
    SKIPPED = "»"
