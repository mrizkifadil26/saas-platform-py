import pytest

from db.config.settings import AppDBSettings, ProductDBSettings


def test_app_db_settings_accepts_valid_url() -> None:
    cfg = AppDBSettings(
        url="postgresql+asyncpg://user:pass@localhost/app_db",
    )

    # assert cfg.pool_size == 10
    # assert cfg.max_overflow == 20
    # assert cfg.pool_timeout == 30
    # assert cfg.pool_recycle == 1800
    assert cfg.url == "postgresql+asyncpg://user:pass@localhost/app_db"


def test_product_db_settings_accepts_valid_url() -> None:
    cfg = ProductDBSettings(
        url="postgresql+asyncpg://user:pass@localhost/product_db",
    )

    # assert cfg.pool_size == 10
    # assert cfg.max_overflow == 20
    assert cfg.url == "postgresql+asyncpg://user:pass@localhost/product_db"


def test_app_db_settings_rejects_empty_url() -> None:
    with pytest.raises(ValueError, match="Database URL cannot be empty"):
        AppDBSettings(url="")


def test_product_db_settings_rejects_empty_url() -> None:
    with pytest.raises(ValueError, match="Database URL cannot be empty"):
        ProductDBSettings(url="")
