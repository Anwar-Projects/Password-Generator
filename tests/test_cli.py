"""Tests for CLI functionality."""

import tempfile
from pathlib import Path

import pytest

from password_generator.cli import create_parser, load_dictionary, main, write_passwords


class TestCreateParser:
    """Tests for argument parser."""

    def test_default_output(self):
        parser = create_parser()
        args = parser.parse_args([])
        assert args.output == "passwords.txt"

    def test_custom_output(self):
        parser = create_parser()
        args = parser.parse_args(["-o", "out.txt"])
        assert args.output == "out.txt"

    def test_dictionary_input(self):
        parser = create_parser()
        args = parser.parse_args(["--dictionary", "a,b,c"])
        assert args.dictionary == "a,b,c"

    def test_flag_combinations(self):
        parser = create_parser()
        args = parser.parse_args(["--no-numbers", "--no-permutations"])
        assert args.no_numbers is True
        assert args.no_permutations is True


class TestLoadDictionary:
    """Tests for dictionary loading."""

    def test_from_string(self):
        result = load_dictionary("apple,banana,car", None)
        assert result == ["apple", "banana", "car"]

    def test_empty_string_returns_empty(self):
        result = load_dictionary("", None)
        assert result == []

    def test_whitespace_trimmed(self):
        result = load_dictionary("  apple  ,  banana  ", None)
        assert result == ["apple", "banana"]

    def test_from_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("apple\\n")
            f.write("banana\\n")
            f.write("# comment\\n")
            f.write("car\\n")
            path = f.name

        result = load_dictionary(None, path)
        assert result == ["apple", "banana", "car"]

        Path(path).unlink()

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_dictionary(None, "/nonexistent/file.txt")


class TestWritePasswords:
    """Tests for password file writing."""

    def test_writes_passwords(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "passwords.txt"
            passwords = {"pass1", "pass2", "pass3"}
            count = write_passwords(passwords, str(path))
            assert count == 3
            assert path.exists()
            content = path.read_text()
            assert "pass1" in content
            assert "pass2" in content

    def test_creates_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subdir" / "passwords.txt"
            count = write_passwords({"test"}, str(path))
            assert path.exists()


class TestMain:
    """Integration tests for main function."""

    def test_help_shows_usage(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out

    def test_version_flag(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_basic_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = str(Path(tmp) / "out.txt")
            code = main(["--dictionary", "apple", "--output", output, "--no-permutations"])
            assert code == 0
            assert Path(output).exists()

    def test_invalid_dictionary_file(self):
        code = main(["--dictionary-file", "/nonexistent/file.txt"])
        assert code == 1
