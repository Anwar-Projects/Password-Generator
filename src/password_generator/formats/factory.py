"""Factory for creating formatters."""

from .base import OutputFormatter
from .json_formatter import JSONFormatter
from .csv_formatter import CSVFormatter
from .hash_formatter import HashFormatter
from .qr_formatter import QRFormatter


FORMATTERS = {
    "json": JSONFormatter,
    "csv": CSVFormatter,
    "hash": HashFormatter,
    "qr": QRFormatter,
    "text": None,  # Plain text, no formatter
}


def get_formatter(
    format_name: str,
    **options
) -> OutputFormatter | None:
    """Get formatter by name.
    
    Args:
        format_name: Format name.
        **options: Formatter options.
        
    Returns:
        Formatter instance or None for plain text.
    """
    format_name = format_name.lower()
    
    if format_name == "text":
        return None
        
    formatter_class = FORMATTERS.get(format_name)
    if not formatter_class:
        raise ValueError(f"Unknown format: {format_name}")
        
    return formatter_class(**options)


def list_formatters() -> dict[str, str]:
    """List available formatters.
    
    Returns:
        Dict mapping names to descriptions.
    """
    return {
        "text": "Plain text (one password per line)",
        "json": "JSON with metadata",
        "csv": "CSV spreadsheet format",
        "hash": "Password hashes (bcrypt, argon2, etc.)",
        "qr": "QR Code images",
    }
