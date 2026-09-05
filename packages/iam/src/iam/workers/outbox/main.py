import asyncio

from db import AppDBSettings, create_engine, create_session_factory
from iam.identity.application.handlers import SendVerificationEmailHandler
from iam.shared.infrastructure.database.uow import SQLAlchemyUnitOfWork
from iam.shared.infrastructure.email.sender import ConsoleEmailSender
from iam.shared.infrastructure.outbox.dispatcher import OutboxDispatcher
from iam.shared.infrastructure.outbox.worker import OutboxWorker


async def main():
    db_cfg = AppDBSettings(
        url="postgresql+asyncpg://postgres:postgres@localhost:5432/app",
    )

    session_factory = create_session_factory(
        create_engine(cfg=db_cfg),
    )
    uow_factory = SQLAlchemyUnitOfWork(session_factory)

    email_sender = ConsoleEmailSender()
    dispatcher = OutboxDispatcher(
        handlers={
            "send_verification": SendVerificationEmailHandler(
                email_sender,
            )
        }
    )

    worker = OutboxWorker(
        dispatcher=dispatcher,
        uow_factory=uow_factory,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
