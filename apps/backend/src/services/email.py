import base64
from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
import httpx
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..core.config import settings

TEMPLATE_FOLDER = Path(__file__).resolve().parent.parent / 'templates' / 'email'
LOGO_DATA_URI = 'data:image/png;base64,' + base64.b64encode(
    (TEMPLATE_FOLDER / 'assets' / 'logo.png').read_bytes()
).decode()

SEND_TIMEOUT_SECONDS = 15


class EmailService:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_FOLDER),
            autoescape=select_autoescape(['html']),
        )
        self.from_email = settings.SMTP_FROM_EMAIL
        self.provider_api_key = settings.EMAIL_PROVIDER_API_KEY or settings.SMTP_PASSWORD
        self.protocol = settings.EMAIL_PROTOCOL or ('smtp' if settings.APP_ENV == 'local' else 'https')

    def _render(self, template_name: str, context: dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render({'logo_data_uri': LOGO_DATA_URI, **context})

    async def _send_via_smtp(self, to: str, subject: str, html: str) -> None:
        message = EmailMessage()
        message['From'] = self.from_email
        message['To'] = to
        message['Subject'] = subject
        message.add_alternative(html, subtype='html')

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_USE_TLS,
            timeout=SEND_TIMEOUT_SECONDS,
        )

    async def _send_via_provider_api(self, to: str, subject: str, html: str) -> None:
        async with httpx.AsyncClient(timeout=SEND_TIMEOUT_SECONDS) as client:
            response = await client.post(
                settings.EMAIL_PROVIDER_API_URL,
                headers={'Authorization': f'Bearer {self.provider_api_key}'},
                json={'from': self.from_email, 'to': [to], 'subject': subject, 'html': html},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f'Email provider rejected the send: {response.text}')

    async def send_template_email(self, to: str, subject: str, template_name: str, context: dict) -> None:
        html = self._render(template_name, context)
        try:
            if self.protocol == 'smtp':
                await self._send_via_smtp(to, subject, html)
            else:
                await self._send_via_provider_api(to, subject, html)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail='Failed to send email') from e


email_service = EmailService()
