"""Tests for transformer functions."""

import pytest

from password_generator.transformers import (
    capitalize_first_letter,
    generate_numbered_words,
    replace_chars,
)


class TestCapitalizeFirstLetter:
    """Tests for capitalize_first_letter function."""

    def test_simple_word(self):
        assert capitalize_first_letter("hello") == "Hello"

    def test_already_capitalized(self):
        assert capitalize_first_letter("Hello") == "Hello"

    def test_all_uppercase(self):
        assert capitalize_first_letter("HELLO") == "Hello"

    def test_single_char(self):
        assert capitalize_first_letter("a") == "A"

    def test_empty_string(self):
        assert capitalize_first_letter("") == ""


class TestReplaceChars:
    """Tests for replace_chars function."""

    def test_basic_replacement(self):
        result = replace_chars("apple", {"a": "@"})
        assert result == "@pple"

    def test_multiple_replacements(self):
        result = replace_chars("apple", {"a": "@", "e": "3"})
        assert result == "@ppl3"

    def test_case_insensitive(self):
        result = replace_chars("Apple", {"a": "@"})
        assert result == "@pple"

    def test_no_match(self):
        result = replace_chars("xyz", {"a": "@"})
        assert result == "xyz"

    def test_word_boundaries(self):
        result = replace_chars("sassy", {"s": "5"})
        assert result == "5a55y"


class TestGenerateNumberedWords:
    """Tests for generate_numbered_words function."""

    def test_single_digit_length(self):
        result = generate_numbered_words({"word"}, 1, ["!", "@"], max_permutations=100)
        assert "word!0" in result
        assert "word@9" in result
        assert "word!5" in result

    def test_max_permutations_limit(self):
        result = generate_numbered_words({"a", "b"}, 2, ["!"], max_permutations=5)
        assert len(result) <= 5

    def test_empty_base(self):
        result = generate_numbered_words(set(), 1, ["!"])
        assert len(result) == 0
