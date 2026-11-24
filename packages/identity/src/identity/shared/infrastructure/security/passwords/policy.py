from dataclasses import dataclass

from .exceptions import PasswordPolicyViolation


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    min_length: int = 12
    max_length: int = 128

    def validate(
        self,
        password: str,
    ) -> None:
        length = len(password)

        if length < self.min_length:
            raise PasswordPolicyViolation(
                f"Password must be at least {self.min_length} characters long."
            )

        if length > self.max_length:
            raise PasswordPolicyViolation(f"Password must not exceed {self.max_length} characters.")
