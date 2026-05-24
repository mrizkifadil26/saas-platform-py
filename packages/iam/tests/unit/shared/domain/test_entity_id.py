from uuid import UUID

import pytest

from iam.shared.domain import EntityId
from iam.shared.domain.exceptions import ValidationError


class UserId(EntityId):
    pass


def test_should_generate_uuid():
    user_id = UserId.generate()

    assert isinstance(user_id, UserId)
    assert isinstance(user_id.value, UUID)


def test_should_create_from_valid_string():
    valid_uuid_str = "123e4567-e89b-12d3-a456-426614174000"
    user_id = UserId.from_string(valid_uuid_str)

    assert isinstance(user_id, UserId)
    assert user_id.value == UUID(valid_uuid_str)


def test_should_raise_validation_error_for_invalid_string():
    invalid_uuid_str = "invalid-uuid"
    with pytest.raises(ValidationError) as exc:
        UserId.from_string(invalid_uuid_str)

    assert "Invalid UserId format" in str(exc.value)


def test_should_compare_entity_ids_by_value():
    uuid_str = "123e4567-e89b-12d3-a456-426614174000"

    user_id1 = UserId.from_string(uuid_str)
    user_id2 = UserId.from_string(uuid_str)

    assert user_id1 == user_id2


def test_should_convert_entity_id_to_string():
    uuid_str = "123e4567-e89b-12d3-a456-426614174000"
    user_id = UserId.from_string(uuid_str)

    assert str(user_id) == uuid_str
