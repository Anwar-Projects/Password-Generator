"""Cryptographically secure random number generation using secrets module."""

import secrets
import string
from typing import Sequence


class SecureRandom:
    """Wrapper around secrets module for cryptographically secure random generation."""

    @staticmethod
    def choice(sequence: Sequence[str]) -> str:
        """Securely choose a random element from a sequence."""
        return secrets.choice(sequence)

    @staticmethod
    def choices(population: Sequence[str], k: int) -> list[str]:
        """Securely choose k random elements from a population."""
        return [secrets.choice(population) for _ in range(k)]

    @staticmethod
    def randbelow(n: int) -> int:
        """Generate a secure random integer in [0, n)."""
        return secrets.randbelow(n)

    @staticmethod
    def randbits(k: int) -> int:
        """Generate a secure random integer with k random bits."""
        return secrets.randbits(k)

    @staticmethod
    def token_hex(nbytes: int = 32) -> str:
        """Generate a secure random hex string."""
        return secrets.token_hex(nbytes)

    @staticmethod
    def token_urlsafe(nbytes: int = 32) -> str:
        """Generate a secure URL-safe token."""
        return secrets.token_urlsafe(nbytes)

    @staticmethod
    def random_string(length: int, alphabet: str | None = None) -> str:
        """Generate a secure random string."""
        chars = alphabet if alphabet else string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def random_password(
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
    ) -> str:
        """Generate a cryptographically secure random password."""
        chars = ""
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_special:
            chars += "!@#$%^*()_+-=[]{}|;:,.?"

        if not chars:
            raise ValueError("At least one character set must be enabled")

        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def shuffle(data: list) -> None:
        """Securely shuffle a list in-place using Fisher-Yates."""
        for i in range(len(data) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            data[i], data[j] = data[j], data[i]
