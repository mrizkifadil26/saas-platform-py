from abc import abstractmethod

from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.shared.domain.repository import Repository
from billing.shared.domain.value_objects.user_id import UserId


class CreditAccountRepository(
    Repository[CreditAccount, CreditAccountId],
):
    # TODO: later we'll use customer_id instead of user_id, but for now we can keep it simple and use user_id
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> CreditAccount | None:
        """Get the credit account for a given user."""
        raise NotImplementedError
