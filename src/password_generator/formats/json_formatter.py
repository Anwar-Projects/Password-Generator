"""JSON output formatter."""

import json
from typing import Optional

from .base import OutputFormatter, PasswordRecord


class JSONFormatter(OutputFormatter):
    """Format passwords as JSON."""
    
    def __init__(self, indent: Optional[int] = 2):
        """Initialize JSON formatter.
        
        Args:
            indent: JSON indentation level (None for compact).
        """
        self.indent = indent
    
    @property
    def format_name(self) -> str:
        return "json"
    
    @property
    def file_extension(self) -> str:
        return ".json"
    
    def format_single(self, record: PasswordRecord) -> str:
        """Format single record as JSON."""
        return json.dumps(record.to_dict(), indent=self.indent)
    
    def format_batch(self, records: list[PasswordRecord]) -> str:
        """Format batch as JSON array."""
        data = [r.to_dict() for r in records]
        return json.dumps({
            "passwords": data,
            "count": len(data),
        }, indent=self.indent)
