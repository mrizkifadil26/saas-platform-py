from billing.domain.credits.models import Wallet
from billing.domain.types import Credits, UserId


def test_wallet_fields():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )

    assert wallet.user_id == UserId("user_123")
    assert wallet.credits == Credits(100)
