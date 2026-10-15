from email.message import EmailMessage

from aiosmtplib import SMTP

from iam.shared.application.email_sender import Any, EmailSender


class MailpitEmailSender(EmailSender):
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 1025,
        from_: str = "noreply@example.com",
    ) -> None:
        self._host = host
        self._port = port
        self._from = from_

    async def send(
        self,
        *,
        to: str,
        subject: str,
        template: str,
        variables: dict[str, Any],
    ) -> None:
        message = EmailMessage()

        message["From"] = self._from
        message["To"] = to
        message["Subject"] = subject

        message.set_content(template)

        smtp = SMTP(
            hostname=self._host,
            port=self._port,
        )

        await smtp.connect()

        try:
            await smtp.send_message(message)
        finally:
            await smtp.quit()
