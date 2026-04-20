import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, make_url, text
from sqlalchemy.engine import Engine


def assert_safe_test_db(url: str) -> None:
    u = make_url(url)
    db = (u.database or "").lower()
    if not db.endswith("_test"):
        raise RuntimeError(f"Refusing to run migration tests on non-test DB: {db}")


def repo_root() -> Path:
    # Adjust to your monorepo: this assumes tests/ is under packages/db/
    parent_path = Path(__file__).resolve().parents[4]
    return parent_path


def alembic_config(sync_url: str) -> Config:
    """
    Build Alembic Config with an explicit URL.
    Critical: do not rely on env.py defaults.
    """
    root = repo_root()
    ini_path = root / "packages" / "db" / "alembic.ini"
    if not ini_path.exists():
        raise FileNotFoundError(f"alembic.ini not found at {ini_path}")

    cfg = Config(str(ini_path))

    # If your alembic.ini uses script_location = db.migrations already, you can skip this.
    # Otherwise set it explicitly:
    # cfg.set_main_option("script_location", "db.migrations")

    cfg.set_main_option("sqlalchemy.url", sync_url)
    return cfg


def get_sync_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL_SYNC")
    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL_SYNC is required.\n"
            "Example: postgresql://postgres:postgres@localhost:5432/app_users_test"
        )

    return url


APP_SCHEMAS = ("auth", "tenant", "entitlements", "audit", "internal", "public")


def reset_db_schemas(engine) -> None:
    with engine.begin() as conn:
        # Drop schemas that migrations use
        for schema in APP_SCHEMAS:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))


def get_current_revision(engine: Engine) -> str | None:
    with engine.connect() as conn:
        # ctx = MigrationContext.configure(conn)
        # return ctx.get_current_revision()
        row = conn.execute(text("SELECT version_num FROM internal.alembic_version")).fetchone()
        return row[0] if row else None


def get_heads(cfg: Config) -> list[str]:
    script = ScriptDirectory.from_config(cfg)
    return list(script.get_heads())


def upgrade(cfg: Config, rev: str = "head") -> None:
    command.upgrade(cfg, rev)


def downgrade(cfg: Config, rev: str) -> None:
    command.downgrade(cfg, rev)


def stamp(cfg: Config, rev: str) -> None:
    command.stamp(cfg, rev)


def list_tables_with_schema(engine) -> set[str]:
    insp = inspect(engine)
    out: set[str] = set()
    for schema in APP_SCHEMAS:
        for t in insp.get_table_names(schema=schema):
            out.add(f"{schema}.{t}")
    return out
