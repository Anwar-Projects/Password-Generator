"""Base classes for output formatters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class PasswordRecord:
    """Record containing password and metadata."""
    password: str
    timestamp: str
    entropy: Optional[float] = None
    strength_score: Optional[int] = None
    strength_level: Optional[str] = None
    generator_type: Optional[str] = None
    crack_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Name of the format."""
        ...
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for this format."""
        ...
    
    @abstractmethod
    def format_single(self, record: PasswordRecord) -> str:
        """Format a single password record.
        
        Args:
            record: Password record to format.
            
        Returns:
            Formatted string.
        """
        ...
    
    @abstractmethod
    def format_batch(self, records: list[PasswordRecord]) -> str:
        """Format multiple password records.
        
        Args:
            records: List of records to format.
            
        Returns:
            Formatted string.
        """
        ...
    
    def format_password(self, password: str, **metadata) -> str:
        """Convenience method to format a password with metadata.
        
        Args:
            password: The password.
            **metadata: Additional metadata.
            
        Returns:
            Formatted string.
        """
        record = PasswordRecord(
            password=password,
            timestamp=datetime.now().isoformat(),
            **metadata
        )
        return self.format_single(record)
