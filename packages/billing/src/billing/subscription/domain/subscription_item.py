from __future__ import annotations

from dataclasses import dataclass

from billing.subscription.domain.exceptions import InvalidSubscriptionItemQuantityError
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


@dataclass(frozen=True, slots=True)
class SubscriptionItem:
    """A billable line item within a subscription."""

    item_id: SubscriptionItemId
    product_code: ProductCode
    feature_code: FeatureCode
    quantity: int = 1

    def __post_init__(self):
        if self.quantity < 1:
            raise InvalidSubscriptionItemQuantityError("Quantity must be at least 1.")

    def change_quantity(self, new_quantity: int) -> SubscriptionItem:
        if new_quantity < 1:
            raise InvalidSubscriptionItemQuantityError(
                "New quantity must be at least 1."
            )

        return SubscriptionItem(
            item_id=self.item_id,
            product_code=self.product_code,
            feature_code=self.feature_code,
            quantity=new_quantity,
        )

    def same_identity_as(self, other: SubscriptionItem) -> bool:
        """Checks if another SubscriptionItem has the same identity (item_id)."""
        return self.item_id == other.item_id
