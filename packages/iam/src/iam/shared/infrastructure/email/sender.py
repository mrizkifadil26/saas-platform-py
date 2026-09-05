from typing import Any


class ConsoleEmailSender:
    async def send(
        self,
        *,
        to: str,
        template: str,
        variables: dict[str, Any],
    ) -> None:
        print(
            f"""
========================================
EMAIL
========================================
To:      {to}
Template:{template}

{variables}
========================================
"""
        )
