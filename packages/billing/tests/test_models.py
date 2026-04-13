from billing.core.models import Wallet
from billing.core.types import Credits, UserId


def test_wallet_fields():
    wallet = Wallet(
        user_id=UserId("user_123"),
        credits=Credits(100),
    )

    assert wallet.user_id == UserId("user_123")
    assert wallet.credits == Credits(100)
