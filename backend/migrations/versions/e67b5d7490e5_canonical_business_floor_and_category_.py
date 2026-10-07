"""canonical business floor and category relations

Revision ID: e67b5d7490e5
Revises: 
Create Date: 2026-10-02 00:16:11.303318
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = 'e67b5d7490e5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if "buildings" not in tables:
        from app.database import Base
        import app.models

        Base.metadata.create_all(bind=connection)
        return

    if "businesses" in tables and "floor_id" not in {
        column["name"] for column in inspector.get_columns("businesses")
    }:
        if "business_locations" not in tables:
            raise RuntimeError("Cannot migrate businesses: legacy business locations are missing")
        invalid = connection.execute(text("""
            SELECT b.id
            FROM businesses AS b
            LEFT JOIN business_locations AS location
                ON location.business_id = b.id AND location.status = 'active'
            LEFT JOIN floors AS floor ON floor.id = location.floor_id
            GROUP BY b.id
            HAVING COUNT(DISTINCT location.floor_id) != 1
                OR SUM(CASE
                    WHEN location.floor_id IS NOT NULL
                    AND (floor.id IS NULL OR floor.building_id != location.building_id)
                    THEN 1 ELSE 0 END) > 0
        """)).fetchall()
        if invalid:
            raise RuntimeError(
                "Cannot migrate: each business must have exactly one active, "
                "building-consistent floor assignment. Business IDs: "
                + ", ".join(str(row[0]) for row in invalid)
            )

        op.add_column("businesses", sa.Column("floor_id", sa.Integer(), nullable=True))
        connection.execute(text("""
            UPDATE businesses
            SET floor_id = (
                SELECT location.floor_id
                FROM business_locations AS location
                WHERE location.business_id = businesses.id
                    AND location.status = 'active'
                ORDER BY location.is_primary DESC, location.id ASC
                LIMIT 1
            )
        """))

    inspector = inspect(connection)
    business_columns = {column["name"] for column in inspector.get_columns("businesses")}
    if "primary_category_id" in business_columns and "business_categories" in tables:
        association_columns = {column["name"] for column in inspector.get_columns("business_categories")}
        if "is_primary" in association_columns:
            connection.execute(text("""
                INSERT INTO business_categories (business_id, category_id, is_primary)
                SELECT business.id, business.primary_category_id, 1
                FROM businesses AS business
                WHERE business.primary_category_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM business_categories AS link
                        WHERE link.business_id = business.id
                            AND link.category_id = business.primary_category_id
                    )
            """))

    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if "buildings" in tables:
        building_columns = {column["name"] for column in inspector.get_columns("buildings")}
        if "image_url" not in building_columns:
            op.add_column("buildings", sa.Column("image_url", sa.String(length=255), nullable=True))
        connection.execute(text("UPDATE buildings SET status = 'active' WHERE status = 'published'"))

    if "categories" in tables:
        category_columns = {column["name"] for column in inspect(connection).get_columns("categories")}
        with op.batch_alter_table("categories", recreate="always") as batch:
            if "parent_id" in category_columns:
                for foreign_key in inspect(connection).get_foreign_keys("categories"):
                    if "parent_id" in foreign_key["constrained_columns"] and foreign_key["name"]:
                        batch.drop_constraint(foreign_key["name"], type_="foreignkey")
                batch.drop_column("parent_id")
            if "image" in category_columns:
                batch.alter_column("image", new_column_name="image_url", existing_type=sa.String(length=255))
            elif "image_url" not in category_columns:
                batch.add_column(sa.Column("image_url", sa.String(length=255), nullable=True))
            if "created_at" not in category_columns:
                batch.add_column(sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
            if "updated_at" not in category_columns:
                batch.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        connection.execute(text("UPDATE categories SET status = 'active' WHERE status = 'published'"))

    inspector = inspect(connection)
    if "floors" in set(inspector.get_table_names()):
        floor_columns = {column["name"]: column for column in inspector.get_columns("floors")}
        if any(row[0] for row in connection.execute(text("SELECT id FROM floors WHERE floor_number IS NULL"))):
            raise RuntimeError("Cannot migrate: every floor must have a floor_number")
        with op.batch_alter_table("floors", recreate="always") as batch:
            if "created_at" not in floor_columns:
                batch.add_column(sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
            if "updated_at" not in floor_columns:
                batch.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
            batch.alter_column("floor_number", existing_type=sa.Integer(), nullable=False)
            if not any(
                set(constraint["column_names"]) == {"building_id", "floor_number"}
                for constraint in inspect(connection).get_unique_constraints("floors")
            ):
                batch.create_unique_constraint("uq_floor_number_per_building", ["building_id", "floor_number"])
        connection.execute(text("UPDATE floors SET status = 'active' WHERE status = 'published'"))

    inspector = inspect(connection)
    business_columns = {column["name"] for column in inspector.get_columns("businesses")}
    with op.batch_alter_table("businesses", recreate="always") as batch:
        if "primary_category_id" in business_columns:
            for foreign_key in inspect(connection).get_foreign_keys("businesses"):
                if "primary_category_id" in foreign_key["constrained_columns"] and foreign_key["name"]:
                    batch.drop_constraint(foreign_key["name"], type_="foreignkey")
            batch.drop_column("primary_category_id")
        batch.alter_column("floor_id", existing_type=sa.Integer(), nullable=False)
        if not any(
            "floor_id" in foreign_key["constrained_columns"]
            for foreign_key in inspect(connection).get_foreign_keys("businesses")
        ):
            batch.create_foreign_key("fk_businesses_floor_id_floors", "floors", ["floor_id"], ["id"])
    if not any(index["column_names"] == ["floor_id"] for index in inspect(connection).get_indexes("businesses")):
        op.create_index("ix_businesses_floor_id", "businesses", ["floor_id"])
    connection.execute(text("UPDATE businesses SET status = 'active' WHERE status = 'published'"))

    if "business_categories" in tables:
        association_columns = {column["name"] for column in inspect(connection).get_columns("business_categories")}
        association_primary_key = inspect(connection).get_pk_constraint("business_categories").get("constrained_columns") or []
        with op.batch_alter_table("business_categories", recreate="always") as batch:
            for index in inspect(connection).get_indexes("business_categories"):
                if "id" in index["column_names"]:
                    batch.drop_index(index["name"])
            for constraint in inspect(connection).get_unique_constraints("business_categories"):
                if set(constraint["column_names"]) == {"business_id", "category_id"} and constraint["name"]:
                    batch.drop_constraint(constraint["name"], type_="unique")
            if "id" in association_columns:
                batch.drop_column("id")
            if "is_primary" in association_columns:
                batch.drop_column("is_primary")
            if association_primary_key != ["business_id", "category_id"]:
                batch.create_primary_key("pk_business_categories", ["business_id", "category_id"])

    inspector = inspect(connection)
    if "business_locations" in set(inspector.get_table_names()):
        op.drop_table("business_locations")
    if "units" in set(inspect(connection).get_table_names()):
        op.drop_table("units")


def downgrade() -> None:
    raise RuntimeError(
        "This migration removes independent legacy location and primary-category "
        "relationships. Restore a database backup to downgrade."
    )