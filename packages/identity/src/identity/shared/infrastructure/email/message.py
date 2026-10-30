from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    recipient: str
    subject: str
    text: str
    html: str