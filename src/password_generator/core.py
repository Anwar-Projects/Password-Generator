"""Core password generation functionality."""

import itertools
import random
import string
from typing import Optional, Set

from .transformers import (
    capitalize_first_letter,
    replace_chars,
    generate_numbered_words,
)


class PasswordGenerator:
    """Configurable password generator with multiple transformation modes."""

    REPLACEMENTS_FULL = {"a": "@", "o": "0", "i": "1", "s": "5"}
    REPLACEMENTS_O = {"o": "0"}
    REPLACEMENTS_I = {"i": "1"}
    REPLACEMENTS_I_BANG = {"i": "!"}
    REPLACEMENTS_S = {"s": "5"}

    def __init__(
        self,
        dictionary: Optional[list[str]] = None,
        max_permutations: int = 100_000,
        seed: Optional[int] = None,
    ):
        """Initialize the password generator."""
        self.dictionary = dictionary or [
            "animal",
            "beautiful",
            "dog",
            "hospital",
            "apple",
            "boy",
            "india",
        ]
        self.max_permutations = max_permutations
        self.all_words: Set[str] = set()
        if seed is not None:
            random.seed(seed)

    def generate_capitalized_and_lowercase(self) -> Set[str]:
        """Generate capitalized and lowercase versions of dictionary words."""
        result = set()
        for word in self.dictionary:
            clean_word = word.lower().strip()
            if clean_word:
                result.add(capitalize_first_letter(clean_word))
                result.add(clean_word)
        return result

    def generate_random_permutations(
        self, existing_words: Set[str], length: int, count: int
    ) -> Set[str]:
        """Generate random character permutations instead of exhaustive ones."""
        result = set()
        alphabet = string.ascii_lowercase

        for _ in range(min(count, self.max_permutations)):
            chars = random.choices(alphabet, k=length)
            word = capitalize_first_letter("".join(chars))
            if word not in existing_words:
                result.add(word)

        return result

    def apply_replacements(self, words: Set[str]) -> Set[str]:
        """Apply all character replacement rules."""
        result = set(words)
        replacements_list = [
            self.REPLACEMENTS_FULL,
            self.REPLACEMENTS_O,
            self.REPLACEMENTS_I,
            self.REPLACEMENTS_I_BANG,
            self.REPLACEMENTS_S,
        ]

        for replacements in replacements_list:
            for word in words:
                result.add(replace_chars(word, replacements))

        final_words = set(result)
        for word in result:
            final_words.add(replace_chars(word, self.REPLACEMENTS_FULL))

        return final_words

    def generate_variations(
        self,
        base_words: Set[str],
        enable_numbers: bool = True,
        enable_special_prefix: bool = True,
        max_digit_length: int = 4,
        separators: Optional[str] = None,
    ) -> Set[str]:
        """Generate all password variations from base words."""
        result = set(base_words)
        default_separators = "!@#$%^\u0026*()_+-=[]{}|;:'\",.<>/?"
        sep_list = list(separators or default_separators)

        if enable_numbers:
            for digit_length in range(1, max_digit_length + 1):
                result.update(
                    generate_numbered_words(
                        base_words, digit_length, sep_list, self.max_permutations
                    )
                )

        if enable_special_prefix:
            for word in list(result)[: self.max_permutations]:
                for digit in range(10):
                    result.add(f"@{word}{digit}")

        if enable_numbers:
            for length in range(1, max_digit_length + 1):
                limited_words = list(result)[: self.max_permutations // 10]
                for word in limited_words:
                    num_combinations = min(10**length, 100)
                    for num in range(num_combinations):
                        formatted_num = str(num).zfill(length)
                        result.add(f"{word}{formatted_num}")

        return result

    def generate_passwords(
        self,
        include_permutations: bool = True,
        permutation_length: int = 4,
        permutation_count: int = 1000,
        enable_numbers: bool = True,
        enable_special_prefix: bool = True,
        max_digit_length: int = 4,
    ) -> Set[str]:
        """Generate all password variations."""
        self.all_words = self.generate_capitalized_and_lowercase()

        if include_permutations:
            perms = self.generate_random_permutations(
                self.all_words, permutation_length, permutation_count
            )
            self.all_words.update(perms)

        self.all_words = self.apply_replacements(self.all_words)

        final_words = self.generate_variations(
            self.all_words,
            enable_numbers=enable_numbers,
            enable_special_prefix=enable_special_prefix,
            max_digit_length=max_digit_length,
        )

        self.all_words.update(final_words)
        return self.all_words
