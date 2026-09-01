import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.logging_config import security_event

# PBKDF2 hashes for documented training accounts. Passwords are never stored in the app.
# Regenerate with scripts/hash_password.py before any shared deployment.
USERS = {
    "learner": {
        "salt": "47e3b245174cc98c244aa153c88a535b",
        "hash": "6eeb360c47c3dbf21c584aac69a1973f60999279a727bc33b44739e2e1c5e0e5",
        "role": "user",
    },
    "reviewer": {
        "salt": "87254fee3fa29af0cc0029e89ed6137e",
        "hash": "eb5008ef2cfeecc6148add09eb05b7e592f164dd38d87b5cbfbf30d4d61fed0f",
        "role": "reviewer",
    },
}


@dataclass(frozen=True)
class User:
    username: str
    role: str


def _password_hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 600_000).hex()


def authenticate(username: str, password: str) -> User | None:
    record = USERS.get(username)
    # Do equivalent expensive work for unknown users to reduce username timing disclosure.
    salt = record["salt"] if record else "00000000000000000000000000000000"
    candidate = _password_hash(password, salt)
    if not record or not hmac.compare_digest(candidate, record["hash"]):
        return None
    return User(username=username, role=record["role"])


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def create_token(user: User, settings: Settings) -> str:
    now = int(time.time())
    payload = _b64(
        json.dumps(
            {
                "sub": user.username,
                "role": user.role,
                "iat": now,
                "exp": now + settings.token_ttl_seconds,
            },
            separators=(",", ":"),
        ).encode()
    )
    signature = _b64(
        hmac.digest(settings.token_secret.get_secret_value().encode(), payload.encode(), "sha256")
    )
    return f"{payload}.{signature}"


def decode_token(token: str, settings: Settings) -> User:
    try:
        payload, signature = token.split(".", 1)
        expected = _b64(
            hmac.digest(
                settings.token_secret.get_secret_value().encode(), payload.encode(), "sha256"
            )
        )
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        padded = payload + "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded))
        if int(claims["exp"]) < int(time.time()):
            raise ValueError("expired")
        record = USERS.get(claims["sub"])
        if not record or claims["role"] != record["role"]:
            raise ValueError("invalid subject")
        return User(claims["sub"], claims["role"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credentials"
        ) from None


bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    settings: Settings = Depends(get_settings),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    return decode_token(credentials.credentials, settings)


def require_reviewer(user: User = Depends(current_user)) -> User:
    if user.role != "reviewer":
        security_event(
            "authorization_failure", username=user.username, reason="reviewer_role_required"
        )
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user
