from api.app import create_app
from api.settings import Settings


def test_create_app_smoke():
    app = create_app(Settings())
    assert app is not None
