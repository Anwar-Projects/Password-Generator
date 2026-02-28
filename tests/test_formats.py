"""Tests for format modules."""

import json
import pytest
from pathlib import Path

from password_generator.formats import (
    get_formatter,
    list_formatters,
    PasswordRecord,
    JSONFormatter,
    CSVFormatter,
)


@pytest.fixture
def sample_record():
    return PasswordRecord(
        password="TestPass123!",
        timestamp="2024-01-15T10:30:00",
        entropy=85.5,
        strength_score=75,
        strength_level="strong",
    )


@pytest.fixture
def sample_records(sample_record):
    return [
        sample_record,
        PasswordRecord(
            password="Another@Pass9",
            timestamp="2024-01-15T10:30:01",
            entropy=72.3,
            strength_score=65,
            strength_level="moderate",
        ),
    ]


class TestPasswordRecord:
    """Tests for password record."""
    
    def test_to_dict_returns_dict(self, sample_record):
        data = sample_record.to_dict()
        assert isinstance(data, dict)
        assert data["password"] == "TestPass123!"
        assert data["entropy"] == 85.5


class TestListFormatters:
    """Tests for format listing."""
    
    def test_returns_dict(self):
        formats = list_formatters()
        assert isinstance(formats, dict)
        assert "json" in formats
        assert "csv" in formats
        assert "text" in formats


class TestGetFormatter:
    """Tests for formatter factory."""
    
    def test_get_json_formatter(self):
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)
    
    def test_get_csv_formatter(self):
        formatter = get_formatter("csv")
        assert isinstance(formatter, CSVFormatter)
    
    def test_get_text_returns_none(self):
        formatter = get_formatter("text")
        assert formatter is None
    
    def test_unknown_format_raises(self):
        with pytest.raises(ValueError):
            get_formatter("unknown")


class TestJSONFormatter:
    """Tests for JSON formatter."""
    
    def test_format_single(self, sample_record):
        formatter = JSONFormatter()
        result = formatter.format_single(sample_record)
        
        data = json.loads(result)
        assert data["password"] == "TestPass123!"
        assert data["entropy"] == 85.5
    
    def test_format_batch(self, sample_records):
        formatter = JSONFormatter()
        result = formatter.format_batch(sample_records)
        
        data = json.loads(result)
        assert data["count"] == 2
        assert len(data["passwords"]) == 2
    
    def test_format_password_with_metadata(self):
        formatter = JSONFormatter()
        result = formatter.format_password(
            "SecretPass!",
            strength_score=80
        )
        
        data = json.loads(result)
        assert data["password"] == "SecretPass!"
        assert data["strength_score"] == 80
    
    def test_compact_format(self, sample_record):
        formatter = JSONFormatter(indent=None)
        result = formatter.format_single(sample_record)
        
        assert "\n  " not in result  # No indentation


class TestCSVFormatter:
    """Tests for CSV formatter."""
    
    def test_format_single(self, sample_record):
        formatter = CSVFormatter()
        result = formatter.format_single(sample_record)
        
        assert "TestPass123!" in result
        assert "2024-01-15T10:30:00" in result
    
    def test_format_batch_has_header(self, sample_records):
        formatter = CSVFormatter()
        result = formatter.format_batch(sample_records)
        
        lines = result.strip().split("\n")
        assert "password" in lines[0]
        assert "timestamp" in lines[0]
        assert len(lines) == 3  # Header + 2 records
    
    def test_tab_delimiter(self, sample_record):
        formatter = CSVFormatter(delimiter="\t")
        result = formatter.format_single(sample_record)
        
        assert "\t" in result


class TestHashFormatter:
    """Tests for hash formatter."""
    
    def test_format_single_includes_hashes(self):
        from password_generator.formats.hash_formatter import HashFormatter
        
        formatter = HashFormatter(algorithms=["sha256"])
        record = PasswordRecord(
            password="test",
            timestamp="2024-01-15T10:30:00"
        )
        result = formatter.format_single(record)
        
        assert "password: test" in result
        assert "sha256:" in result
    
    def test_format_batch_separates_records(self):
        from password_generator.formats.hash_formatter import HashFormatter
        
        formatter = HashFormatter(algorithms=["sha256"])
        records = [
            PasswordRecord(password="test1", timestamp="2024-01-15T10:30:00"),
            PasswordRecord(password="test2", timestamp="2024-01-15T10:30:01"),
        ]
        result = formatter.format_batch(records)
        
        assert "---" in result


class TestQRFormatter:
    """Tests for QR formatter."""
    
    def test_format_name(self):
        from password_generator.formats.qr_formatter import QRFormatter
        
        formatter = QRFormatter()
        assert formatter.format_name == "qr"
    
    def test_format_single_masks_password(self):
        from password_generator.formats.qr_formatter import QRFormatter
        
        formatter = QRFormatter()
        record = PasswordRecord(
            password="Secret123!",
            timestamp="2024-01-15T10:30:00"
        )
        result = formatter.format_single(record)
        
        # Should mask most of password
        assert "****" in result
        assert "Secr" in result
    
    def test_save_qr_creates_file(self, tmp_path):
        from password_generator.formats.qr_formatter import QRFormatter
        
        formatter = QRFormatter()
        output_path = tmp_path / "test_qr.png"
        
        saved_path = formatter.save_qr("test_password", output_path)
        
        assert saved_path.exists()
        assert saved_path.suffix == ".png"
