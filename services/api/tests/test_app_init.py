from fastapi.testclient import TestClient

from api.app import create_app
from api.settings import Settings


def test_create_app_smoke():
    app = create_app(Settings())
    assert app is not None


def test_lifespan_runs():
    app = create_app(Settings())

    with TestClient(app) as client:
        assert hasattr(app.state, "app_users_sessionmaker")
        r = client.get("/health")

        assert r.status_code == 200