"""Hash output formatter (bcrypt, scrypt, argon2, PBKDF2)."""

import base64
import hashlib
import secrets

import bcrypt
from argon2 import PasswordHasher

from .base import OutputFormatter, PasswordRecord


class HashFormatter(OutputFormatter):
    """Format passwords with cryptographic hashes."""
    
    HASH_ALGORITHMS = ["bcrypt", "argon2", "scrypt", "pbkdf2", "sha256", "sha512"]
    
    def __init__(self, algorithms: list[str] | None = None):
        """Initialize hash formatter.
        
        Args:
            algorithms: List of hash algorithms to use.
        """
        algorithms = algorithms or ["bcrypt"]
        self.algorithms = [
            a for a in algorithms if a in self.HASH_ALGORITHMS
        ]
        self._argon2_hasher = PasswordHasher()
    
    @property
    def format_name(self) -> str:
        return "hash"
    
    @property
    def file_extension(self) -> str:
        return ".hash"
    
    def _hash_bcrypt(self, password: str) -> str:
        """Hash with bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def _hash_argon2(self, password: str) -> str:
        """Hash with Argon2."""
        return self._argon2_hasher.hash(password)
    
    def _hash_scrypt(self, password: str) -> str:
        """Hash with scrypt."""
        salt = secrets.token_bytes(16)
        N = 2**14  # CPU/memory cost
        r = 8      # Block size
        p = 1      # Parallelization
        
        hash_bytes = hashlib.scrypt(
            password.encode(),
            salt=salt,
            n=N,
            r=r,
            p=p,
            dklen=64
        )
        return f"scrypt${N}${r}${p}${base64.b64encode(salt).decode()}" \
               f"${base64.b64encode(hash_bytes).decode()}"
    
    def _hash_pbkdf2(self, password: str, iterations: int = 100000) -> str:
        """Hash with PBKDF2."""
        salt = secrets.token_bytes(16)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            iterations,
            dklen=32
        )
        return f"pbkdf2_sha256${iterations}$" \
               f"{base64.b64encode(salt).decode()}${base64.b64encode(hash_bytes).decode()}"
    
    def _hash_sha256(self, password: str) -> str:
        """Hash with SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _hash_sha512(self, password: str) -> str:
        """Hash with SHA512."""
        return hashlib.sha512(password.encode()).hexdigest()
    
    def _hash_password(self, password: str) -> dict[str, str]:
        """Generate all requested hashes."""
        hashes = {}
        for algo in self.algorithms:
            if algo == "bcrypt":
                hashes["bcrypt"] = self._hash_bcrypt(password)
            elif algo == "argon2":
                hashes["argon2"] = self._hash_argon2(password)
            elif algo == "scrypt":
                hashes["scrypt"] = self._hash_scrypt(password)
            elif algo == "pbkdf2":
                hashes["pbkdf2"] = self._hash_pbkdf2(password)
            elif algo == "sha256":
                hashes["sha256"] = self._hash_sha256(password)
            elif algo == "sha512":
                hashes["sha512"] = self._hash_sha512(password)
        return hashes
    
    def format_single(self, record: PasswordRecord) -> str:
        """Format single record with hashes."""
        hashes = self._hash_password(record.password)
        lines = [f"password: {record.password}"]
        for algo, hash_val in hashes.items():
            lines.append(f"{algo}: {hash_val}")
        return "\n".join(lines)
    
    def format_batch(self, records: list[PasswordRecord]) -> str:
        """Format batch with all hashes."""
        lines = []
        for record in records:
            lines.append(self.format_single(record))
            lines.append("---")
        return "\n".join(lines)
