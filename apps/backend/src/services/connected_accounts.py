import json
import hmac
import base64
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.crypto import encrypt, decrypt
from ..models.connected_account import ConnectedAccount
from ..models.user import User

# ── Google OAuth scopes ───────────────────────────────────────────────────────

GOOGLE_BASE_SCOPES = ['openid', 'email', 'profile']

FEATURE_SCOPES: dict[str, list[str]] = {
    'gmail': [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.settings.basic',
    ],
    'calendar': [
        'https://www.googleapis.com/auth/calendar.events',
    ],
}

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'


# ── State signing (tamper-proof OAuth state param) ────────────────────────────

def _sign_state(payload: dict) -> str:
    data = json.dumps(payload, separators=(',', ':'))
    encoded = base64.urlsafe_b64encode(data.encode()).decode()
    sig = hmac.new(settings.AUTH_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f'{encoded}.{sig}'


def verify_state(state: str) -> dict | None:
    try:
        encoded, sig = state.rsplit('.', 1)
        expected = hmac.new(settings.AUTH_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(base64.urlsafe_b64decode(encoded).decode())
    except Exception:
        return None


# ── Core service functions ────────────────────────────────────────────────────

def upsert(
    db: Session,
    user_id: int,
    provider: str,
    provider_user_id: str,
    provider_email: str | None,
    display_name: str | None,
    avatar_url: str | None,
    access_token: str | None,
    refresh_token: str | None,
    expires_in: int | None,
    scopes: list[str],
) -> ConnectedAccount:
    account = db.query(ConnectedAccount).filter_by(user_id=user_id, provider=provider).first()

    encrypted_access = encrypt(access_token) if access_token else None
    encrypted_refresh = encrypt(refresh_token) if refresh_token else None
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        if expires_in else None
    )

    if account:
        account.provider_user_id = provider_user_id
        if provider_email:
            account.provider_email = provider_email
        if display_name:
            account.display_name = display_name
        if avatar_url:
            account.avatar_url = avatar_url
        if encrypted_access:
            account.access_token = encrypted_access
        # Only overwrite refresh_token when a new one is issued
        if encrypted_refresh:
            account.refresh_token = encrypted_refresh
        if expires_at:
            account.token_expires_at = expires_at
        # Merge scopes (never shrink — only expand)
        merged = list({*( account.scopes or []), *scopes})
        account.scopes = merged
        account.last_used_at = datetime.now(timezone.utc)
    else:
        account = ConnectedAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            display_name=display_name,
            avatar_url=avatar_url,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            token_expires_at=expires_at,
            scopes=scopes,
            connected_at=datetime.now(timezone.utc),
            last_used_at=datetime.now(timezone.utc),
        )
        db.add(account)

    db.commit()
    db.refresh(account)
    return account


def get_by_provider_user_id(db: Session, provider: str, provider_user_id: str) -> ConnectedAccount | None:
    return db.query(ConnectedAccount).filter_by(
        provider=provider, provider_user_id=provider_user_id
    ).first()


def get_user_by_provider(db: Session, provider: str, provider_user_id: str) -> User | None:
    account = get_by_provider_user_id(db, provider, provider_user_id)
    if not account:
        return None
    return db.query(User).filter_by(id=account.user_id).first()


def list_for_user(db: Session, user_id: int) -> list[ConnectedAccount]:
    return db.query(ConnectedAccount).filter_by(user_id=user_id).all()


def disconnect(db: Session, user_id: int, provider: str) -> bool:
    account = db.query(ConnectedAccount).filter_by(user_id=user_id, provider=provider).first()
    if not account:
        return False
    db.delete(account)
    db.commit()
    return True


def get_decrypted_tokens(account: ConnectedAccount) -> tuple[str | None, str | None]:
    access = decrypt(account.access_token) if account.access_token else None
    refresh = decrypt(account.refresh_token) if account.refresh_token else None
    return access, refresh


# ── OAuth URL builders ────────────────────────────────────────────────────────

def _google_redirect_uri() -> str:
    return f'{settings.BACKEND_URL}/api/v1/auth/google/callback'


def google_auth_url(origin: str = 'web', user_id: int | None = None, features: list[str] | None = None) -> str:
    purpose = 'upgrade' if user_id else 'login'
    payload: dict = {'origin': origin, 'purpose': purpose, 'nonce': secrets.token_urlsafe(8)}
    if user_id:
        payload['user_id'] = user_id

    requested_scopes = list(GOOGLE_BASE_SCOPES)
    for feature in (features or []):
        requested_scopes.extend(FEATURE_SCOPES.get(feature, []))

    params: dict = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': _google_redirect_uri(),
        'response_type': 'code',
        'scope': ' '.join(requested_scopes),
        'state': _sign_state(payload),
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        # Force consent so Google re-issues a refresh token on scope upgrades
        'prompt': 'consent' if purpose == 'upgrade' else 'select_account',
    }
    return f'{GOOGLE_AUTH_URL}?{urlencode(params)}'
