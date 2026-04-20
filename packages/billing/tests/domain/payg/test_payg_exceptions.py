# packages/billing/tests/domain/payg/test_exceptions.py

from billing.domain.payg.exceptions import (
    PaygDomainError,
    UnknownPaygPack,
)


def test_unknown_payg_pack_subclasses_payg_domain_error():
    assert issubclass(UnknownPaygPack, PaygDomainError)
