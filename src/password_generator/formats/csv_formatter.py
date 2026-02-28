"""CSV output formatter."""

import csv
import io

from .base import OutputFormatter, PasswordRecord


class CSVFormatter(OutputFormatter):
    """Format passwords as CSV."""
    
    def __init__(self, delimiter: str = ","):
        """Initialize CSV formatter.
        
        Args:
            delimiter: Field delimiter.
        """
        self.delimiter = delimiter
    
    @property
    def format_name(self) -> str:
        return "csv"
    
    @property
    def file_extension(self) -> str:
        return ".csv"
    
    def format_single(self, record: PasswordRecord) -> str:
        """Format single record as CSV row."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self.delimiter)
        writer.writerow([
            record.password,
            record.timestamp,
            record.entropy or "",
            record.strength_score or "",
            record.strength_level or "",
        ])
        return output.getvalue().strip()
    
    def format_batch(self, records: list[PasswordRecord]) -> str:
        """Format batch as CSV with header."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self.delimiter)
        
        # Header
        writer.writerow([
            "password",
            "timestamp",
            "entropy",
            "strength_score",
            "strength_level",
            "generator_type",
            "crack_time",
        ])
        
        # Records
        for record in records:
            writer.writerow([
                record.password,
                record.timestamp,
                record.entropy or "",
                record.strength_score or "",
                record.strength_level or "",
                record.generator_type or "",
                record.crack_time or "",
            ])
            
        return output.getvalue()
