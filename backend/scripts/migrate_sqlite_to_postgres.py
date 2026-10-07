from __future__ import annotations

import argparse

from sqlalchemy import create_engine, func, select, text

from app.core.config import settings
from app.database import Base
import app.models


def migrate(source_url: str) -> int:
    source = create_engine(source_url)
    target = create_engine(settings.database_url)
    try:
        if source.dialect.name != "sqlite" or target.dialect.name != "postgresql":
            raise ValueError("Source must be SQLite and DATABASE_URL must point to PostgreSQL")

        with source.connect() as source_connection, target.begin() as target_connection:
            source_tables = set(source_connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).scalars())
            if "alembic_version" not in source_tables:
                raise ValueError("Run Alembic migrations on the SQLite source before importing it")

            target_tables = set(target_connection.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = current_schema()
            """)).scalars())
            if "alembic_version" not in target_tables:
                raise ValueError("Run `python -m alembic upgrade head` on PostgreSQL before importing")

            for table in Base.metadata.sorted_tables:
                if table.name not in source_tables or table.name not in target_tables:
                    raise ValueError(f"Migrated table is missing: {table.name}")
                if target_connection.execute(select(func.count()).select_from(table)).scalar_one():
                    raise ValueError(
                        f"PostgreSQL table {table.name} is not empty; refusing to mix datasets"
                    )

            imported = 0
            for table in Base.metadata.sorted_tables:
                rows = source_connection.execute(select(table)).mappings().all()
                if rows:
                    target_connection.execute(table.insert(), [dict(row) for row in rows])
                    imported += len(rows)

            for table in Base.metadata.sorted_tables:
                if "id" not in table.c:
                    continue
                target_connection.execute(
                    text("""
                        SELECT setval(
                            pg_get_serial_sequence(:table_name, 'id'),
                            COALESCE((SELECT MAX(id) FROM """ + table.name + """), 1),
                            EXISTS (SELECT 1 FROM """ + table.name + """)
                        )
                    """),
                    {"table_name": table.name},
                )
        return imported
    finally:
        source.dispose()
        target.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy a migrated SQLite database into an empty PostgreSQL database.")
    parser.add_argument("source_url", help="SQLite SQLAlchemy URL for the migrated source database")
    arguments = parser.parse_args()
    print(f"Imported {migrate(arguments.source_url)} rows into PostgreSQL.")