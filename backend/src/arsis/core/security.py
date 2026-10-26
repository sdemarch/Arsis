"""Password hashing and token primitives for the authentication boundary."""

import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from arsis.core.time import utc_now

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "arsis-api"
JWT_AUDIENCE = "arsis-frontend"
_REFRESH_TOKEN_BYTES = 48
_password_hash = PasswordHash.recommended()
_DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$"
    "CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc"
)


class InvalidAccessTokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str | None) -> tuple[bool, str | None]:
    """Verify a password and return an upgraded hash when its parameters are obsolete."""

    candidate_hash = password_hash or _DUMMY_HASH
    try:
        return _password_hash.verify_and_update(password, candidate_hash)
    except UnknownHashError:
        _password_hash.verify(password, _DUMMY_HASH)
        return False, None


def create_access_token(
    user_id: str,
    *,
    secret_key: str,
    ttl_seconds: int,
    now: datetime | None = None,
) -> str:
    issued_at = now or utc_now()
    payload = {
        "sub": user_id,
        "type": "access",
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": issued_at,
        "exp": issued_at + timedelta(seconds=ttl_seconds),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, *, secret_key: str) -> str:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require": ["sub", "type", "iat", "exp", "jti"]},
        )
    except InvalidTokenError as exception:
        raise InvalidAccessTokenError("Access token non valido") from exception

    subject = payload.get("sub")
    if payload.get("type") != "access" or not isinstance(subject, str) or not subject:
        raise InvalidAccessTokenError("Access token non valido")
    return subject


def create_refresh_token() -> str:
    return secrets.token_urlsafe(_REFRESH_TOKEN_BYTES)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

