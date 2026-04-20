from db.config.settings import AppDBSettings, ProductDBSettings


def test_app_settings_defaults():
    cfg = AppDBSettings(database_url="postgresql+asyncpg://user:pass@localhost/app")

    assert cfg.pool_size == 10
    assert cfg.max_overflow == 20
    assert cfg.pool_timeout == 30
    assert cfg.pool_recycle == 1800


def test_product_settings_defaults():
    cfg = ProductDBSettings(database_url="postgresql+asyncpg://user:pass@localhost/product")

    assert cfg.pool_size == 10
    assert cfg.max_overflow == 20
