from db.app_db.base import AppBase


def test_app_base_has_metadata() -> None:
    assert AppBase.metadata is not None
