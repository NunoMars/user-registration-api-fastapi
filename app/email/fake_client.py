import logging

from app.email.client import EmailClient

logger = logging.getLogger(__name__)


class FakeEmailClient:
    async def send_activation_code(self, email: str, code: str) -> None:
        logger.info("Fake activation email sent", extra={"email": email, "code": code})
        print(f"[FAKE EMAIL] To: {email} | Activation code: {code}")


def get_email_client() -> EmailClient:
    return FakeEmailClient()
