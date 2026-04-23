from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """Base class for specifications."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the candidate satisfies the specification."""
        raise NotImplementedError("Subclasses must implement this method.")

    def __call__(self, candidate: T) -> bool:
        """Allow the specification to be called as a function."""
        return self.is_satisfied_by(candidate)

    def __and__(self, other: Specification[T]) -> Specification[T]:
        """Combine this specification with another using logical AND."""
        return AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        """Combine this specification with another using logical OR."""
        return OrSpecification(self, other)
    
    def __invert__(self) -> Specification[T]:
        """Negate this specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Specification that combines two specifications with logical AND."""

    def __init__(self, spec1: Specification[T], spec2: Specification[T]) -> None:
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.spec1.is_satisfied_by(candidate) and self.spec2.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """Specification that combines two specifications with logical OR."""

    def __init__(self, spec1: Specification[T], spec2: Specification[T]) -> None:
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.spec1.is_satisfied_by(candidate) or self.spec2.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """Specification that negates another specification."""

    def __init__(self, spec: Specification[T]) -> None:
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)