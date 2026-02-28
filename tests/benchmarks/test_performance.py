"""Performance benchmarks for password generator."""

import pytest

from password_generator.security.secrets_wrapper import SecureRandom
from password_generator.core import PasswordGenerator
from password_generator.security.diceware import DicewareGenerator
from password_generator.security.entropy import calculate_entropy


class TestGenerationBenchmark:
    """Benchmark password generation performance."""
    
    def bench_generate_random_passwords(self, benchmark):
        """Benchmark random password generation."""
        def generate():
            return SecureRandom.random_password(16)
        
        benchmark(generate)
    
    def bench_generate_bulk_passwords(self, benchmark):
        """Benchmark bulk password generation."""
        def generate():
            return [
                SecureRandom.random_password(16)
                for _ in range(100)
            ]
        
        benchmark(generate)
    
    def bench_generate_different_lengths(self, benchmark):
        """Benchmark password generation at different lengths."""
        def generate():
            return {
                8: SecureRandom.random_password(8),
                16: SecureRandom.random_password(16),
                32: SecureRandom.random_password(32),
                64: SecureRandom.random_password(64),
            }
        
        benchmark(generate)


class TestEntropyBenchmark:
    """Benchmark entropy calculation performance."""
    
    def bench_calculate_entropy_short(self, benchmark):
        """Benchmark entropy for short password."""
        benchmark(calculate_entropy, "Test123!")
    
    def bench_calculate_entropy_long(self, benchmark):
        """Benchmark entropy for long password."""
        benchmark(calculate_entropy, "ThisIsAVeryLongPasswordWithSpecial123!")
    
    def bench_calculate_entropy_batch(self, benchmark):
        """Benchmark bulk entropy calculation."""
        passwords = [
            "password123",
            "Tr0ub4dor3",
            "correcthorsebatterystaple",
            "P@$$w0rd!2024",
        ]
        def calc_all():
            return [calculate_entropy(p) for p in passwords]
        benchmark(calc_all)


class TestDicewareBenchmark:
    """Benchmark diceware passphrase generation."""
    
    def bench_generate_passphrase(self, benchmark):
        """Benchmark passphrase generation."""
        generator = DicewareGenerator()
        benchmark(lambda: list(generator.generate(6, 1))[0])
    
    def bench_generate_xkcd_passphrase(self, benchmark):
        """Benchmark XKCD-style passphrase generation."""
        generator = DicewareGenerator()
        benchmark(generator.generate_xkcd_style, 4, " ")


class TestTransformBenchmark:
    """Benchmark transformation operations."""
    
    def bench_capitalize_word(self, benchmark):
        """Benchmark capitalization."""
        from password_generator.transformers import capitalize_first_letter
        benchmark(capitalize_first_letter, "password123")
    
    def bench_replace_chars(self, benchmark):
        """Benchmark character replacement."""
        from password_generator.transformers import replace_chars
        replacements = {"a": "@", "e": "3", "i": "1"}
        benchmark(replace_chars, "password", replacements)
