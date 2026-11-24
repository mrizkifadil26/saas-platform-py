from email.message import EmailMessage as MIMEEmail

import aiosmtplib

from identity.shared.infrastructure.email.message import EmailMessage


class SMTPEmailSender:
    def __init__(
        self,
        *,
        hostname: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        sender: str,
        use_tls: bool = False,
        start_tls: bool = True,
    ) -> None:
        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._sender = sender
        self._use_tls = use_tls
        self._start_tls = start_tls

    async def send(self, email: EmailMessage) -> None:
        message = MIMEEmail()

        message["From"] = self._sender
        message["To"] = email.recipient
        message["Subject"] = email.subject

        message.set_content(email.text)
        message.add_alternative(
            email.html,
            subtype="html",
        )

        await aiosmtplib.send(
            message,
            hostname=self._hostname,
            port=self._port,
            username=self._username,
            password=self._password,
            use_tls=self._use_tls,
            start_tls=self._start_tls,
        )
