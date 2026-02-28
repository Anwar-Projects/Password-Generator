"""Built-in output plugins."""

import json
from pathlib import Path

from .base import OutputPlugin


class FileOutput(OutputPlugin):
    """Output to file."""
    
    name = "file"
    description = "Write passwords to file"
    
    def write(self, passwords: list[str], destination: str, **options) -> None:
        mode = options.get("mode", "w")
        with open(destination, mode) as f:
            for pwd in passwords:
                f.write(f"{pwd}\n")
    
    def supports(self, destination: str) -> bool:
        try:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False


class JSONOutput(OutputPlugin):
    """Output to JSON file."""
    
    name = "json"
    description = "Write passwords as JSON"
    
    def write(self, passwords: list[str], destination: str, **options) -> None:
        include_metadata = options.get("include_metadata", True)
        
        data = {
            "passwords": passwords,
            "count": len(passwords),
        }
        
        if include_metadata:
            data["metadata"] = {
                "format": "json",
                "version": "2.0",
            }
        
        with open(destination, "w") as f:
            json.dump(data, f, indent=2)
    
    def supports(self, destination: str) -> bool:
        return destination.endswith(".json")


class CSVOutput(OutputPlugin):
    """Output to CSV file."""
    
    name = "csv"
    description = "Write passwords as CSV"
    
    def write(self, passwords: list[str], destination: str, **options) -> None:
        import csv
        
        with open(destination, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["password"])
            for pwd in passwords:
                writer.writerow([pwd])
    
    def supports(self, destination: str) -> bool:
        return destination.endswith(".csv")


class HashOutput(OutputPlugin):
    """Output password hashes."""
    
    name = "hash"
    description = "Write password hashes"
    
    def write(self, passwords: list[str], destination: str, **options) -> None:
        algorithms = options.get("algorithms", ["bcrypt"])
        from ..formats.hash_formatter import HashFormatter
        
        formatter = HashFormatter(algorithms)
        from ..formats.base import PasswordRecord
        from datetime import datetime
        
        records = [
            PasswordRecord(
                password=pwd,
                timestamp=datetime.now().isoformat()
            )
            for pwd in passwords
        ]
        
        content = formatter.format_batch(records)
        with open(destination, "w") as f:
            f.write(content)
    
    def supports(self, destination: str) -> bool:
        return destination.endswith(".hash")


class QROutput(OutputPlugin):
    """Output QR codes."""
    
    name = "qr"
    description = "Generate QR code images"
    
    def write(self, passwords: list[str], destination: str, **options) -> None:
        from ..formats.qr_formatter import QRFormatter
        
        formatter = QRFormatter()
        
        for i, pwd in enumerate(passwords):
            output_path = f"{destination}_{i:03d}.png"
            formatter.save_qr(pwd, output_path)
    
    def supports(self, destination: str) -> bool:
        return True  # Directory path
