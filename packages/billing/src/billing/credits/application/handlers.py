from billing.credits.application.commands import (
    ConsumeReservedCreditsCommand,
    CreateCreditAccountCommand,
    ExpireCreditsCommand,
    GrantCreditsCommand,
    PurchaseCreditsCommand,
    ReleaseReservedCreditsCommand,
    ReserveCreditsCommand,
)
from billing.credits.application.dto import CreditAccountDTO
from billing.credits.application.exceptions import (
    CreditAccountAlreadyExistsError,
    CreditAccountNotFoundError,
)
from billing.credits.application.mappers import CreditAccountMapper
from billing.credits.domain.credit_account import CreditAccount
from billing.credits.domain.credit_source_type import CreditSourceType
from billing.credits.domain.value_objects.credit_account_id import CreditAccountId
from billing.credits.domain.value_objects.credit_grant_id import CreditGrantId
from billing.credits.domain.value_objects.credits import Credits
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW


class CreateCreditAccountHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        id_generator: IdGenerator,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._event_publisher = event_publisher

        # self.idempotency_store = idempotency_store

    async def handle(
        self,
        command: CreateCreditAccountCommand,
    ) -> CreditAccountDTO:
        async with self._uow as uow:
            existing = await uow.credit_accounts.get_by_user_id(command.user_id)

            if existing is not None:
                raise CreditAccountAlreadyExistsError(
                    f"Credit account already exists for user_id={command.user_id}"
                )

            account = CreditAccount.create(
                id=CreditAccountId(self._id_generator.generate()),
                user_id=command.user_id,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class GrantCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        id_generator: IdGenerator,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: GrantCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.grant(
                grant_id=CreditGrantId(self._id_generator.generate()),
                amount=Credits.of(command.amount),
                occurred_at=self._clock.now(),
                expires_at=command.expires_at,
                source_type=command.source_type,
                source_id=command.source_id,
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class PurchaseCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        id_generator: IdGenerator,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: PurchaseCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.grant(
                grant_id=CreditGrantId(self._id_generator.generate()),
                amount=Credits.of(command.amount),
                occurred_at=self._clock.now(),
                expires_at=command.expires_at,
                source_type=CreditSourceType.PURCHASE,
                source_id=command.source_id,
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class ReserveCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: ReserveCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.reserve(
                amount=Credits.of(command.amount),
                occurred_at=self._clock.now(),
                source_id=command.source_id,
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class ConsumeReservedCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: ConsumeReservedCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.consume_reserved(
                amount=Credits.of(command.amount),
                occurred_at=self._clock.now(),
                source_id=command.source_id,
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class ReleaseReservedCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: ReleaseReservedCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.release_reserved(
                amount=Credits.of(command.amount),
                occurred_at=self._clock.now(),
                source_id=command.source_id,
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)


class ExpireCreditsHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

    async def handle(self, command: ExpireCreditsCommand) -> CreditAccountDTO:
        async with self._uow as uow:
            account = await uow.credit_accounts.get_by_user_id(command.user_id)

            if account is None:
                raise CreditAccountNotFoundError(
                    f"Credit account not found for user_id={command.user_id}"
                )

            account.expire_grants(
                occurred_at=self._clock.now(),
                description=command.description,
            )

            await uow.credit_accounts.save(account)
            await uow.commit()

        events = account.pull_domain_events()
        self._event_publisher.publish(events)

        return CreditAccountMapper.domain_to_dto(account)
