# Billing Package

A Python package for handling billing operations, including pay-as-you-go and subscription plans.

## Features

- Pay-as-you-go plans with credit packs
- Subscription plans with monthly billing
- Credit charging with idempotency support
- Custom error types for billing operations

## Installation

This package is part of the larger project and should be installed via Poetry from the project root.

## Usage

### Getting Plans

```python
from billing import get_payg_plan, get_subscription_plan, PlanCode

# Get a pay-as-you-go plan
payg_plan = get_payg_plan(PlanCode("payg_10_usd"))
print(f"Credits: {payg_plan.credits_grant}, Price: ${payg_plan.price_cents / 100}")

# Get a subscription plan
sub_plan = get_subscription_plan(PlanCode("sub_basic_monthly"))
print(f"Credits: {sub_plan.credits_grant}, Price: ${sub_plan.price_cents / 100}")
```

### Charging Credits

```python
from billing import charge_credits, Credits, RequestId

# Simple charge
new_balance = charge_credits(Credits(1000), Credits(100))
print(f"New balance: {new_balance}")

# Charge with idempotency
used_ids = set()
new_balance = charge_credits(
    Credits(1000),
    Credits(100),
    RequestId("unique-request-id"),
    used_ids
)
```

## Error Handling

```python
from billing import (
    InsufficientCredits,
    UnknownPlan,
    IdempotencyConflict,
    get_payg_plan,
    charge_credits,
    PlanCode,
    Credits
)

try:
    plan = get_payg_plan(PlanCode("invalid"))
except UnknownPlan as e:
    print(f"Unknown plan: {e}")

try:
    charge_credits(Credits(50), Credits(100))
except InsufficientCredits as e:
    print(f"Insufficient credits: {e}")
```

## Available Plans

### Pay-as-you-go Plans

| Code | Tier | Credits | Price (USD) |
|------|------|---------|-------------|
| payg_10_usd | pack_10 | 100 | 10 |
| payg_50_usd | pack_50 | 600 | 50 |
| payg_100_usd | pack_100 | 1300 | 100 |
| payg_500_usd | pack_500 | 7500 | 500 |
| payg_1000_usd | pack_1000 | 17000 | 1000 |

### Subscription Plans

| Code | Tier | Credits | Price (USD) | Interval |
|------|------|---------|-------------|----------|
| sub_basic_monthly | basic | 1000 | 99 | month |
| sub_pro_monthly | pro | 5000 | 299 | month |
| sub_enterprise_monthly | enterprise | 20000 | 999 | month |

## Development

Run tests:
```bash
poetry run pytest
```

Run type checking:
```bash
poetry run mypy .
```