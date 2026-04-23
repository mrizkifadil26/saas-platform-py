from pathlib import Path

from alembic import command
from alembic.config import Config


def _build_config(
    script_location: str,
    database_url: str,
) -> Config:
    config = Config()
    config.set_main_option("script_location", script_location)
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def test_app_db_migration_structure_exists() -> None:
    base = Path("src/db/alembic_app/app_db")

    assert base.exists()
    assert (base / "env.py").exists()
    assert (base / "versions").exists()


def test_app_db_migrations_upgrade() -> None:
    config = _build_config(
        script_location="src/db/alembic_app/app_db",
        database_url="sqlite:///./test_app_migrations.db",
    )
    command.upgrade(config, "head")
