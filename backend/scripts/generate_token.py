#!/usr/bin/env python3
"""Generate a test JWT for local development.

Usage:
    python scripts/generate_token.py

Outputs a valid JWT that can be used in the Authorization header:
    Authorization: Bearer <token>

Requires NEXTAUTH_SECRET to be set in your .env file.
"""

import sys
from datetime import datetime, timedelta, timezone

import jwt

# Load settings — this requires the .env file to be present.
from app.config import settings

EXPIRY_HOURS = 24


def main() -> None:
    payload = {
        "email": "admin@d3jusdevspace.com",
        "sub": "admin@d3jusdevspace.com",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=EXPIRY_HOURS),
    }

    token = jwt.encode(payload, settings.nextauth_secret, algorithm="HS256")

    print("\n--- d3jusdevspace Test JWT ---")
    print(f"Email:   {payload['email']}")
    print(f"Expires: {payload['exp'].isoformat()}")
    print(f"\nToken:\n{token}")
    print(f"\ncurl header:")
    print(f'  -H "Authorization: Bearer {token}"')
    print()


if __name__ == "__main__":
    main()
