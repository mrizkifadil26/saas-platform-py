from dataclasses import dataclass

from iam.shared.domain import Entity


@dataclass(eq=False)
class User(Entity[int]):
    name: str


@dataclass(eq=False)
class Product(Entity[int]):
    title: str


def test_should_compare_entities_by_id():
    user1 = User(id=1, name="Alice")
    user2 = User(id=1, name="Bob")
    user3 = User(id=2, name="Alice")

    assert user1 == user2
    assert user1 != user3


def test_should_not_compare_entities_with_different_ids():
    user1 = User(id=1, name="Alice")
    user2 = User(id=2, name="Bob")

    assert user1 != user2


def test_should_not_compare_entities_with_different_types():
    user = User(id=1, name="Alice")
    product = Product(id=1, title="Product 1")

    assert user != product


def test_should_generate_same_hash_for_same_id():
    user1 = User(id=1, name="Alice")
    user2 = User(id=1, name="Bob")

    assert hash(user1) == hash(user2)


def test_should_generate_different_hash_for_different_ids():
    user1 = User(id=1, name="Alice")
    user2 = User(id=2, name="Bob")

    assert hash(user1) != hash(user2)

def test_should_generate_different_hash_for_different_types():
    user = User(id=1, name="Alice")
    product = Product(id=1, title="Product 1")

    assert hash(user) != hash(product)