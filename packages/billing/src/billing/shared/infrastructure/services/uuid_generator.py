import uuid

from billing.shared.application.id_generator import IdGenerator


class UUIDGenerator(IdGenerator):
    def generate(self) -> str:
        return str(uuid.uuid4())
