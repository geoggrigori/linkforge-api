"""Short code generation."""

import secrets

# URL-safe, unambiguous alphabet (no 0/O/1/l/I) to avoid transcription errors.
_ALPHABET = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"


def generate_code(length: int = 7) -> str:
    """Return a random short code, e.g. 'k7Qm2pf'."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
