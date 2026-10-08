from typing import Any

from iam.shared.application.email_sender import EmailSender


class ConsoleEmailSender(EmailSender):
    async def send(
        self,
        *,
        to: str,
        subject: str,
        template: str,
        variables: dict[str, Any],
    ) -> None:
        print(
            f"""
========================================
EMAIL
========================================
To:      {to}
Subject: {subject}
Template:{template}

{variables}
========================================
"""
        )
