from billing.pricing.application.handlers import (
    CreatePricingSnapshotHandler,
    GetPricingRuleHandler,
)


def get_pricing_rule_handler() -> GetPricingRuleHandler:
    raise NotImplementedError("Wire this in your DI container")


def get_create_pricing_snapshot_handler() -> CreatePricingSnapshotHandler:
    raise NotImplementedError("Wire this in your DI container")
