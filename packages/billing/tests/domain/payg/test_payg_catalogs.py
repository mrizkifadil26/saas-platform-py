import pytest

from billing.domain.credits.value_objects import Credits
from billing.domain.payg.catalogs import (
    PaygPack,
    get_payg_pack,
)
from billing.domain.payg.exceptions import UnknownPaygPack
from billing.domain.shared.value_objects import PlanCode


def test_get_payg_pack_returns_known_pack_with_expected_credits_and_price():
    pack = get_payg_pack(PlanCode("payg_10_usd"))

    assert isinstance(pack, PaygPack)
    assert pack.code == PlanCode("payg_10_usd")
    assert pack.credits == Credits(100)


def test_get_payg_pack_unknown():
    with pytest.raises(UnknownPaygPack):
        get_payg_pack(PlanCode("unknown"))
