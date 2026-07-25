import asyncio
import base64
from pathlib import Path

from fastapi import HTTPException
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from ..core.config import settings

TEMPLATE_FOLDER = Path(__file__).resolve().parent.parent / 'templates' / 'email'
LOGO_DATA_URI = 'data:image/png;base64,' + base64.b64encode(
    (TEMPLATE_FOLDER / 'assets' / 'logo.png').read_bytes()
).decode()

SEND_TIMEOUT_SECONDS = 15


class EmailService:
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USERNAME,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=settings.SMTP_USE_TLS,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=bool(settings.SMTP_USERNAME),
            TEMPLATE_FOLDER=TEMPLATE_FOLDER,
            TIMEOUT=SEND_TIMEOUT_SECONDS,
        )
        self.mailer = FastMail(self.config)

    async def send_template_email(self, to: str, subject: str, template_name: str, context: dict) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            template_body={'logo_data_uri': LOGO_DATA_URI, **context},
            subtype=MessageType.html,
        )
        try:
            await asyncio.wait_for(
                self.mailer.send_message(message, template_name=template_name),
                timeout=SEND_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=503, detail='Timed out sending email')


email_service = EmailService()
