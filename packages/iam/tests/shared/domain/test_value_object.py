from iam.shared.domain import ValueObject


class StringValueObject(ValueObject[str]):
    pass


def test_should_unwrap_value():
    value_object = StringValueObject("test")
    assert value_object.unwrap() == "test"


def test_should_convert_to_string():
    value_object = StringValueObject("test")
    assert str(value_object) == "test"


def test_should_have_repr():
    value_object = StringValueObject("test")
    assert repr(value_object) == "StringValueObject('test')"


def test_should_be_immutable():
    value_object = StringValueObject("test")

    try:
        value_object.value = "new value"  # type: ignore
    except AttributeError as exc:
        assert isinstance(exc, Exception)
    else:
        assert False, "ValueObject should be immutable"
