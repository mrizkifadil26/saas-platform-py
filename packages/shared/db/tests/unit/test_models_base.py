from db.models.base import Base, TimestampMixin


def test_base_has_metadata():
    assert Base.metadata is not None


def test_timestamp_mixin_has_columns():
    assert "created_at" in TimestampMixin.__dict__
    assert "updated_at" in TimestampMixin.__dict__
