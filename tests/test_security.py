"""Tests for security module."""

import pytest

from password_generator.security.secrets_wrapper import SecureRandom
from password_generator.security.entropy import calculate_entropy, estimate_crack_time, analyze_patterns
from password_generator.security.validator import PasswordValidator, StrengthLevel
from password_generator.security.diceware import DicewareGenerator, load_wordlist


class TestSecureRandom:
    """Tests for SecureRandom wrapper."""
    
    def test_choice_returns_element(self):
        items = ["a", "b", "c"]
        result = SecureRandom.choice(items)
        assert result in items
    
    def test_choices_returns_correct_count(self):
        items = ["x", "y", "z"]
        results = SecureRandom.choices(items, 5)
        assert len(results) == 5
        assert all(r in items for r in results)
    
    def test_random_string_length(self):
        length = 20
        result = SecureRandom.random_string(length)
        assert len(result) == length
    
    def test_random_password_default(self):
        pw = SecureRandom.random_password()
        assert len(pw) == 16
        assert any(c.isupper() for c in pw)
        assert any(c.islower() for c in pw)
        assert any(c.isdigit() for c in pw)
    
    def test_randbelow_range(self):
        result = SecureRandom.randbelow(100)
        assert 0 <= result < 100
    
    def test_shuffle_modifies_list(self):
        items = [1, 2, 3, 4, 5]
        original = items.copy()
        SecureRandom.shuffle(items)
        assert len(items) == len(original)
        assert set(items) == set(original)


class TestEntropy:
    """Tests for entropy calculation."""
    
    def test_calculate_entropy_returns_result(self):
        result = calculate_entropy("password")
        assert result.entropy > 0
        assert result.pool_size > 0
        assert result.category in ["very_weak", "weak", "moderate", "strong", "very_strong", "excellent"]
    
    def test_longer_passwords_have_higher_entropy(self):
        short = calculate_entropy("abc123")
        long = calculate_entropy("ThisIsAVeryLongPassword123!")
        assert long.entropy > short.entropy
    
    def test_estimate_crack_time_returns_result(self):
        result = estimate_crack_time("password123")
        assert result.seconds > 0
        assert len(result.human_readable) > 0
        assert result.level in ["critical", "weak", "moderate", "strong", "very_strong", "excellent"]
    
    def test_empty_password_entropy(self):
        result = calculate_entropy("")
        assert result.entropy == 0
        assert result.category == "empty"
    
    def test_analyze_patterns_detects_sequences(self):
        result = analyze_patterns("abc123")
        assert result["sequential_letters"] or result["sequential_numbers"] or result["keyboard_patterns"]
    
    def test_different_character_sets_increase_entropy(self):
        lower = calculate_entropy("abcdefgh")
        mixed = calculate_entropy("AbC123!@")
        assert mixed.entropy > lower.entropy


class TestPasswordValidator:
    """Tests for password validator."""
    
    def test_validate_returns_strength_score(self):
        validator = PasswordValidator()
        result = validator.validate("P@ssw0rd!")
        assert isinstance(result.score, int)
        assert 0 <= result.score <= 100
        assert isinstance(result.level, StrengthLevel)
    
    def test_weak_password_low_score(self):
        validator = PasswordValidator()
        result = validator.validate("password")
        assert result.score < 50
    
    def test_strong_password_high_score(self):
        validator = PasswordValidator()
        result = validator.validate("Tr0ub4dor3#Secure!2024")
        assert result.score >= 60
    
    def test_common_password_fails(self):
        validator = PasswordValidator()
        result = validator.validate("password123")
        assert "common_password" in result.failed_checks
    
    def test_min_length_check(self):
        validator = PasswordValidator(min_length=12)
        result = validator.validate("short")
        assert "length" in result.failed_checks
    
    def test_character_variety_check(self):
        validator = PasswordValidator(require_digits=True)
        result = validator.validate("NoDigitsHere")
        assert "digits" in result.failed_checks
    
    def test_is_strong_enough_returns_bool(self):
        validator = PasswordValidator()
        assert validator.is_strong_enough("Str0ng!Pass#word2024")
        assert not validator.is_strong_enough("weak")


class TestDicewareGenerator:
    """Tests for diceware generator."""
    
    def test_generate_returns_correct_word_count(self):
        generator = DicewareGenerator()
        passphrase = list(generator.generate(6, 1))[0]
        words = passphrase.split(generator.separator)
        assert len(words) == 6
    
    def test_generate_xkcd_style_returns_four_words(self):
        generator = DicewareGenerator()
        passphrase = generator.generate_xkcd_style(4, " ")
        words = passphrase.split(" ")
        assert len(words) == 4
    
    def test_capitalize_changes_case(self):
        generator = DicewareGenerator(capitalize=True)
        passphrase = list(generator.generate(4, 1))[0]
        words = passphrase.split(generator.separator)
        assert all(w[0].isupper() for w in words if w)
    
    def test_load_wordlist_returns_list(self):
        words = load_wordlist()
        assert len(words) > 0
        assert all(isinstance(w, str) for w in words)
    
    def test_consistent_separator(self):
        generator = DicewareGenerator(separator="_")
        passphrase = list(generator.generate(4, 1))[0]
        assert "_" in passphrase
