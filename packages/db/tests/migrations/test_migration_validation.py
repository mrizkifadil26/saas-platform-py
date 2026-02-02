"""
Migration & Schema Validation

This test suite enforces:
1) Migration history is sane (single head)
2) A fresh database can be migrated to the latest revision
3) The migrated schema matches SQLAlchemy models (no drift)

Required env var:
- TEST_DATABASE_URL_SYNC (sync driver URL)
  Example: postgresql://postgres:postgres@localhost:5432/app_users_test

Notes:
- This test DROPS and recreates the public schema on the test DB.
- Safety guardrail: DB name must end with _test.
"""

from __future__ import annotations


import pytest
from sqlalchemy import create_engine, inspect

from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.autogenerate import compare_metadata

# ---- Import your Base.metadata (DeclarativeBase) ----
# Adjust import if your Base lives elsewhere.
from db.models.base import Base
from tests.migrations._alembic_utils import (
    alembic_config,
    assert_safe_test_db,
    get_current_revision,
    get_sync_url,
    list_tables_with_schema,
    reset_db_schemas,
)


pytestmark = pytest.mark.migration

# A couple of tables that MUST exist after migrating to head.
# Add more if you want stronger guarantees.
EXPECTED_TABLES = {"auth.sessions"}

# -----------------------------
# tests
# -----------------------------


def test_migration_history_has_single_head():
    """
    Prevents migration conflicts where two PRs introduce different heads.
    Fix by creating a merge revision if needed:
      alembic merge -m "merge heads" <head1> <head2>
    """
    url = get_sync_url()
    assert_safe_test_db(url)

    cfg = alembic_config(url)
    script = ScriptDirectory.from_config(cfg)

    heads = list(script.get_heads())
    assert len(heads) == 1, f"Multiple heads detected: {heads}"


def test_empty_database_upgrades_to_head():
    """
    Ensures a brand-new database can be created from migrations alone.
    """
    url = get_sync_url()
    assert_safe_test_db(url)

    cfg = alembic_config(url)
    engine = create_engine(url, future=True)

    reset_db_schemas(engine)
    command.upgrade(cfg, "head")

    # revision table should exist and have a current revision
    rev = get_current_revision(engine)
    assert rev is not None, "Expected alembic_version to be set after upgrade"

    # minimal schema sanity checks
    tables = list_tables_with_schema(engine)
    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing expected tables after upgrade: {missing}"

    engine.dispose()


def test_schema_matches_models():
    """
    Detects drift between SQLAlchemy models (Base.metadata) and migrated DB schema.
    If this fails, you likely:
    - changed models without creating a migration, OR
    - created a migration that doesn't match the models (type/nullable/default/index mismatch).
    """
    url = get_sync_url()
    assert_safe_test_db(url)

    cfg = alembic_config(url)
    engine = create_engine(url, future=True)

    reset_db_schemas(engine)
    command.upgrade(cfg, "head")

    with engine.connect() as conn:
        ctx = MigrationContext.configure(
            conn,
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "include_schemas": True,
                "version_table_schema": "internal",
            },
        )
        diffs = compare_metadata(ctx, Base.metadata)

    assert diffs == [], (
        "Schema drift detected (models != migrated schema). "
        "Generate/fix a migration.\n"
        f"Diffs: {diffs}"
    )

    engine.dispose()
