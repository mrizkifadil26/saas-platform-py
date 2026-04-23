# packages/billing/tests/domain/payg/test_domain_services.py

from datetime import timedelta

import pytest
from billing.domain.credits.value_objects import GrantId
from billing.domain.payg.domain_services import (
    PAYG_EXPIRY_DAYS,
    create_payg_purchase,
)
from billing.domain.payg.exceptions import UnknownPaygPack
from billing.domain.payg.value_objects import PaygPurchaseId
from billing.domain.shared.value_objects import PlanCode


def test_create_payg_purchase_raises_on_unknown_plan_code(
    now,
    user_id,
    request_id,
):
    with pytest.raises(UnknownPaygPack):
        create_payg_purchase(
            grant_id=GrantId.new(),
            purchase_id=PaygPurchaseId.new(),
            user_id=user_id,
            plan_code=PlanCode("unknown"),
            request_id=request_id,
            now=now,
        )


def test_create_payg_purchase_returns_payg_purchase_with_passed_ids_user_and_request_id(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert result.purchase.purchase_id is not None
    assert result.purchase.user_id == user_id
    assert result.purchase.plan_code == PlanCode(
        "payg_10_usd"
    )
    assert result.purchase.request_id == request_id


def test_create_payg_purchase_returns_credit_grant_with_source_payg(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert result.grant.source == "payg"


def test_create_payg_purchase_sets_grant_remaining_equal_granted_equal_pack_credits(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert (
        result.grant.remaining_credits
        == result.grant.granted_credits
    )
    assert (
        result.grant.granted_credits == result.event.credits
    )


def test_create_payg_purchase_sets_grant_expiry_to_now_plus_payg_expiry_days(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert result.grant.expires_at == now + timedelta(
        days=PAYG_EXPIRY_DAYS
    )


def test_create_payg_purchase_adds_plan_code_into_grant_metadata(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert (
        result.grant.metadata["plan_code"] == "payg_10_usd"
    )


def test_create_payg_purchase_copies_caller_metadata_instead_of_mutating_it(
    now,
    user_id,
    request_id,
):
    metadata = {"source": "checkout"}

    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
        metadata=metadata,
    )

    assert result.purchase.metadata == {
        "source": "checkout"
    }
    assert metadata == {"source": "checkout"}
    assert result.purchase.metadata is not metadata


def test_create_payg_purchase_emits_payg_credits_granted_with_pack_credits_and_request_id(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
    )

    assert result.event.user_id == user_id
    assert result.event.plan_code == PlanCode("payg_10_usd")
    assert result.event.request_id == request_id
    assert (
        result.event.credits == result.grant.granted_credits
    )


def test_create_payg_purchase_keeps_event_metadata_equal_to_cleaned_input_metadata(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
        metadata={"source": "checkout"},
    )

    assert result.event.metadata == {"source": "checkout"}


def test_create_payg_purchase_keeps_purchase_metadata_equal_to_cleaned_input_metadata(
    now,
    user_id,
    request_id,
):
    result = create_payg_purchase(
        grant_id=GrantId.new(),
        purchase_id=PaygPurchaseId.new(),
        user_id=user_id,
        plan_code=PlanCode("payg_10_usd"),
        request_id=request_id,
        now=now,
        metadata={"source": "checkout"},
    )

    assert result.purchase.metadata == {
        "source": "checkout"
    }
