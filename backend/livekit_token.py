"""
Generate a LiveKit Access Token (JWT) using HMAC-SHA256.

This produces a JWT with a small set of claims that LiveKit accepts for room join.
If you prefer, replace this with the official LiveKit server SDK.
"""
import os
import time
from uuid import uuid4
import jwt
from typing import Optional


def create_access_token(api_key: str, api_secret: str, identity: str, room: Optional[str] = None, ttl: int = 3600) -> str:
    now = int(time.time())
    payload = {
        "jti": str(uuid4()),
        "iss": api_key,
        "sub": api_key,
        "nbf": now,
        "iat": now,
        "exp": now + ttl,
        # LiveKit expects grants describing identity/room/permissions. Keep minimal.
        "grants": {
            "identity": identity,
        },
    }
    if room:
        payload["grants"]["room"] = room

    token = jwt.encode(payload, api_secret, algorithm="HS256")
    # jwt.encode returns str in pyjwt>=2.x
    return token
