from typing import Protocol


class EmailClient(Protocol):
    async def send_activation_code(self, email: str, code: str) -> None:
        """Send an activation code to a user email address."""
