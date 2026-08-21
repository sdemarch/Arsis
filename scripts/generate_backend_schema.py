"""Generate SQLAlchemy models and Pydantic DTOs from the migrated SQLite schema."""

from __future__ import annotations

import argparse
import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE: Final = PROJECT_ROOT / "data" / "arsis.db"
DEFAULT_OUTPUT: Final = PROJECT_ROOT / "backend" / "src" / "arsis" / "generated"
IGNORED_TABLES: Final = {"databasechangelog", "databasechangeloglock"}


@dataclass(frozen=True)
class Column:
    name: str
    declared_type: str
    nullable: bool
    default: str | None
    primary_key: bool


@dataclass(frozen=True)
class ForeignKeyDefinition:
    target_table: str
    target_column: str
    on_delete: str | None


@dataclass(frozen=True)
class TableDefinition:
    name: str
    columns: tuple[Column, ...]
    foreign_keys: dict[str, ForeignKeyDefinition]


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def class_name(table_name: str) -> str:
    exceptions = {"people": "person"}
    words = table_name.split("_")
    last = exceptions.get(words[-1], words[-1])
    if last.endswith("ies"):
        last = last[:-3] + "y"
    elif last.endswith("sses"):
        last = last[:-2]
    elif last.endswith("s") and not last.endswith("ss"):
        last = last[:-1]
    words[-1] = last
    return "".join(word.capitalize() for word in words)


def read_schema(database_path: Path) -> tuple[tuple[TableDefinition, ...], str]:
    if not database_path.is_file():
        raise FileNotFoundError(
            f"Database non trovato: {database_path}. Eseguire prima scripts/init-db.ps1."
        )

    with sqlite3.connect(database_path) as connection:
        table_rows = connection.execute(
            """
            SELECT name, sql
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        application_rows = [
            (name, sql)
            for name, sql in table_rows
            if name.casefold() not in IGNORED_TABLES
        ]
        definitions: list[TableDefinition] = []

        for table_name, _ in application_rows:
            table_literal = quote_identifier(table_name)
            column_rows = connection.execute(f"PRAGMA table_xinfo({table_literal})").fetchall()
            foreign_key_rows = connection.execute(
                f"PRAGMA foreign_key_list({table_literal})"
            ).fetchall()
            foreign_keys = {
                row[3]: ForeignKeyDefinition(
                    target_table=row[2],
                    target_column=row[4],
                    on_delete=None if row[6] == "NO ACTION" else row[6],
                )
                for row in foreign_key_rows
            }
            columns = tuple(
                Column(
                    name=row[1],
                    declared_type=row[2] or "TEXT",
                    nullable=not bool(row[3]) and not bool(row[5]),
                    default=row[4],
                    primary_key=bool(row[5]),
                )
                for row in column_rows
                if row[6] == 0
            )
            definitions.append(TableDefinition(table_name, columns, foreign_keys))

    schema_source = "\n".join(f"{name}\n{sql or ''}" for name, sql in application_rows)
    fingerprint = hashlib.sha256(schema_source.encode("utf-8")).hexdigest()[:16]
    return tuple(definitions), fingerprint


def python_and_sqlalchemy_types(column: Column) -> tuple[str, str]:
    declared_type = column.declared_type.upper()
    if declared_type.startswith("INTEGER") and column.name.startswith("is_"):
        return "bool", "Boolean"
    if "INT" in declared_type:
        return "int", "Integer"
    if any(token in declared_type for token in ("NUMERIC", "DECIMAL")):
        return "Decimal", "Numeric"
    if any(token in declared_type for token in ("REAL", "FLOAT", "DOUBLE")):
        return "float", "Float"
    if "BLOB" in declared_type:
        return "bytes", "LargeBinary"
    return "str", "Text"


def column_annotation(column: Column, *, force_optional: bool = False) -> str:
    python_type, _ = python_and_sqlalchemy_types(column)
    if column.nullable or force_optional:
        return f"{python_type} | None"
    return python_type


def render_model_column(table: TableDefinition, column: Column) -> str:
    python_type, sqlalchemy_type = python_and_sqlalchemy_types(column)
    annotation = f"{python_type} | None" if column.nullable else python_type
    arguments = [sqlalchemy_type]
    foreign_key = table.foreign_keys.get(column.name)
    if foreign_key:
        options = ""
        if foreign_key.on_delete:
            options = f", ondelete={foreign_key.on_delete!r}"
        target = f"{foreign_key.target_table}.{foreign_key.target_column}"
        arguments.append(f"ForeignKey({target!r}{options})")

    options = [f"primary_key={column.primary_key!r}", f"nullable={column.nullable!r}"]
    if column.default is not None:
        options.append(f"server_default=text({column.default!r})")
    call_arguments = ", ".join([*arguments, *options])
    return f"    {column.name}: Mapped[{annotation}] = mapped_column({call_arguments})"


def render_models(tables: tuple[TableDefinition, ...], fingerprint: str) -> str:
    imports = {
        sqlalchemy_type
        for table in tables
        for column in table.columns
        for _, sqlalchemy_type in [python_and_sqlalchemy_types(column)]
    }
    if any(table.foreign_keys for table in tables):
        imports.add("ForeignKey")
    if any(column.default is not None for table in tables for column in table.columns):
        imports.add("text")
    sqlalchemy_imports = ", ".join(sorted(imports))
    needs_decimal = any(
        python_and_sqlalchemy_types(column)[0] == "Decimal"
        for table in tables
        for column in table.columns
    )

    lines = [
        '"""Generated SQLAlchemy models. Do not edit by hand."""',
        "# ruff: noqa",
        "",
        "from __future__ import annotations",
        "",
    ]
    if needs_decimal:
        lines.extend(["from decimal import Decimal", ""])
    lines.extend(
        [
            f"from sqlalchemy import {sqlalchemy_imports}",
            "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column",
            "",
            f'SCHEMA_FINGERPRINT = "{fingerprint}"',
            "",
            "",
            "class Base(DeclarativeBase):",
            "    pass",
        ]
    )

    exported_names = ["Base", "SCHEMA_FINGERPRINT"]
    for table in tables:
        model_name = class_name(table.name)
        exported_names.append(model_name)
        lines.extend(["", "", f"class {model_name}(Base):", f'    __tablename__ = "{table.name}"', ""])
        lines.extend(render_model_column(table, column) for column in table.columns)

    lines.extend(["", "", f"__all__ = {exported_names!r}"])
    return "\n".join(lines) + "\n"


SERVER_MANAGED_FIELDS: Final = {
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
    "archived_at",
    "archived_by",
    "version",
}


def create_columns(table: TableDefinition) -> tuple[Column, ...]:
    return tuple(
        column
        for column in table.columns
        if column.name != "id" and column.name not in SERVER_MANAGED_FIELDS
    )


def render_dto_field(column: Column, *, update: bool = False, read: bool = False) -> str:
    annotation = column_annotation(column, force_optional=update)
    if update:
        return f"    {column.name}: {annotation} = None"
    if read:
        return f"    {column.name}: {annotation}"
    if column.nullable or column.default is not None:
        return f"    {column.name}: {annotation if column.nullable else annotation + ' | None'} = None"
    return f"    {column.name}: {annotation}"


def render_dtos(tables: tuple[TableDefinition, ...], fingerprint: str) -> str:
    needs_decimal = any(
        python_and_sqlalchemy_types(column)[0] == "Decimal"
        for table in tables
        for column in table.columns
    )
    lines = [
        '"""Generated Pydantic persistence DTOs. Do not edit by hand."""',
        "# ruff: noqa",
        "",
        "from __future__ import annotations",
        "",
    ]
    if needs_decimal:
        lines.extend(["from decimal import Decimal", ""])
    lines.extend(
        [
            "from pydantic import BaseModel, ConfigDict",
            "",
            f'SCHEMA_FINGERPRINT = "{fingerprint}"',
            "",
            "",
            "class GeneratedDTO(BaseModel):",
            '    model_config = ConfigDict(extra="forbid", from_attributes=True)',
        ]
    )

    exported_names = ["GeneratedDTO", "SCHEMA_FINGERPRINT"]
    for table in tables:
        prefix = class_name(table.name)
        create_name = f"{prefix}CreateDTO"
        update_name = f"{prefix}UpdateDTO"
        read_name = f"{prefix}ReadDTO"
        exported_names.extend([create_name, update_name, read_name])
        writable_columns = create_columns(table)
        updatable_columns = tuple(
            column for column in writable_columns if not column.primary_key
        )

        lines.extend(["", "", f"class {create_name}(GeneratedDTO):"])
        if writable_columns:
            lines.extend(render_dto_field(column) for column in writable_columns)
        else:
            lines.append("    pass")

        lines.extend(["", "", f"class {update_name}(GeneratedDTO):"])
        if updatable_columns:
            lines.extend(render_dto_field(column, update=True) for column in updatable_columns)
        else:
            lines.append("    pass")

        lines.extend(["", "", f"class {read_name}(GeneratedDTO):"])
        lines.extend(render_dto_field(column, read=True) for column in table.columns)

    lines.extend(["", "", f"__all__ = {exported_names!r}"])
    return "\n".join(lines) + "\n"


def render_init() -> str:
    return '''"""Database code generated from the migrated SQLite schema."""

from .models import SCHEMA_FINGERPRINT, Base

__all__ = ["Base", "SCHEMA_FINGERPRINT"]
'''


def synchronize(output_directory: Path, contents: dict[str, str], *, check: bool) -> bool:
    stale_files = [
        name
        for name, content in contents.items()
        if not (output_directory / name).is_file()
        or (output_directory / name).read_text(encoding="utf-8") != content
    ]
    if check:
        if stale_files:
            print("File generati non allineati: " + ", ".join(stale_files))
            return False
        print("Modelli SQLAlchemy e DTO Pydantic allineati allo schema.")
        return True

    output_directory.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        path = output_directory / name
        if name in stale_files:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"Generato: {path.relative_to(PROJECT_ROOT)}")
    if not stale_files:
        print("Nessuna modifica: codice backend già allineato allo schema.")
    return True


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Non scrive file e termina con errore se il codice generato non è aggiornato.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    database_path = arguments.database.resolve()
    output_directory = arguments.output.resolve()
    tables, fingerprint = read_schema(database_path)
    if not tables:
        raise RuntimeError(f"Nessuna tabella applicativa trovata in {database_path}.")
    contents = {
        "__init__.py": render_init(),
        "models.py": render_models(tables, fingerprint),
        "schemas.py": render_dtos(tables, fingerprint),
    }
    return 0 if synchronize(output_directory, contents, check=arguments.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
