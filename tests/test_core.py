"""Tests for core password generator functionality."""

import pytest

from password_generator.core import PasswordGenerator
from password_generator.transformers import generate_numbered_words


class TestPasswordGeneratorInit:
    """Tests for PasswordGenerator initialization."""

    def test_default_initialization(self):
        gen = PasswordGenerator()
        assert gen.dictionary is not None
        assert gen.max_permutations == 100_000

    def test_custom_dictionary(self):
        custom_dict = ["one", "two", "three"]
        gen = PasswordGenerator(dictionary=custom_dict)
        assert gen.dictionary == custom_dict

    def test_custom_max_permutations(self):
        gen = PasswordGenerator(max_permutations=500)
        assert gen.max_permutations == 500

    def test_seed_reproducibility(self):
        gen1 = PasswordGenerator(seed=42)
        gen2 = PasswordGenerator(seed=42)
        perm1 = gen1.generate_random_permutations(set(), 4, 10)
        perm2 = gen2.generate_random_permutations(set(), 4, 10)
        assert perm1 == perm2


class TestGenerateCapitalizedAndLowercase:
    """Tests for capitalization generation."""

    def test_basic_words(self):
        gen = PasswordGenerator(dictionary=["apple", "BANANA"])
        result = gen.generate_capitalized_and_lowercase()
        assert "apple" in result
        assert "Apple" in result
        assert "banana" in result
        assert "Banana" in result

    def test_whitespace_handling(self):
        gen = PasswordGenerator(dictionary=["  apple  ", ""])
        result = gen.generate_capitalized_and_lowercase()
        assert "apple" in result
        assert "Apple" in result
        assert "" not in result


class TestGenerateRandomPermutations:
    """Tests for random permutation generation."""

    def test_generates_unique_words(self):
        gen = PasswordGenerator()
        existing = {"Apple", "Banana"}
        result = gen.generate_random_permutations(existing, 4, 50)
        # Should not overlap with existing
        assert len(result & existing) == 0
        assert len(result) <= 50

    def test_respects_max_permutations(self):
        gen = PasswordGenerator(max_permutations=10)
        result = gen.generate_random_permutations(set(), 4, 100)
        assert len(result) <= 10

    def test_length_consistency(self):
        gen = PasswordGenerator()
        result = gen.generate_random_permutations(set(), 5, 10)
        for word in result:
            assert len(word) == 5  # First letter capitalized doesn't add length


class TestApplyReplacements:
    """Tests for character replacement."""

    def test_replacements_applied(self):
        gen = PasswordGenerator(dictionary=["apple"])
        base = gen.generate_capitalized_and_lowercase()
        result = gen.apply_replacements(base)
        # Should include words with @ for 'a'
        assert any("@" in w for w in result)


class TestGeneratePasswords:
    """Integration tests for full password generation."""

    def test_smoke_test(self):
        """Basic smoke test that generation completes."""
        gen = PasswordGenerator(dictionary=["cat"] , max_permutations=1000)
        passwords = gen.generate_passwords(
            include_permutations=False,
            enable_numbers=False,
            enable_special_prefix=False,
        )
        assert len(passwords) > 0

    def test_with_permutations(self):
        gen = PasswordGenerator(dictionary=["a"] , max_permutations=100)
        passwords = gen.generate_passwords(
            include_permutations=True,
            permutation_count=5,
            enable_numbers=False,
            enable_special_prefix=False,
        )
        assert len(passwords) > 0


class TestPerformanceLimits:
    """Tests that ensure performance limits are respected."""

    def test_permutation_limit_prevents_infinite_loop(self):
        """Critical test: ensures max_permutations prevents runaway computation."""
        gen = PasswordGenerator(max_permutations=50)
        # Even with large digit length, should complete quickly
        result = generate_numbered_words({"word"}, 4, ["!"], max_permutations=50)
        assert len(result) <= 50
