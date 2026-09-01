#!/usr/bin/env python3
"""Generate a PBKDF2 record; paste only its salt/hash into the educational user store."""

import getpass
import hashlib
import secrets

password = getpass.getpass("Password: ")
salt = secrets.token_bytes(16)
print(
    {
        "salt": salt.hex(),
        "hash": hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000).hex(),
    }
)
