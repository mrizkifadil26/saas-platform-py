from identity.shared.infrastructure.email.message import EmailMessage


class ConsoleEmailSender:
    async def send(self, email: EmailMessage) -> None:
        print("=" * 60)
        print(f"To: {email.recipient}")
        print(f"Subject: {email.subject}")
        print()
        print(email.text)
        print("=" * 60)
