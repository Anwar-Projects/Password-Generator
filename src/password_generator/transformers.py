"""Text transformation utilities for password generation."""

import itertools
from typing import Set


def capitalize_first_letter(word: str) -> str:
    """Capitalize the first letter of a word.

    Args:
        word: Input word.

    Returns:
        Word with first letter capitalized.
    """
    if not word:
        return word
    return word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper()


def replace_chars(word: str, replacements: dict[str, str]) -> str:
    """Replace characters in a word based on a mapping.

    Args:
        word: Input word.
        replacements: Dictionary mapping characters to their replacements.

    Returns:
        Word with characters replaced.
    """
    result = word.lower()
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def generate_numbered_words(
    base_words: Set[str],
    digit_length: int,
    separators: list[str],
    max_permutations: int = 100_000,
) -> Set[str]:
    """Generate words with numbered suffixes and separators.

    Args:
        base_words: Set of base words.
        digit_length: Length of digit suffix.
        separators: List of separator characters.
        max_permutations: Maximum number of combinations to generate.

    Returns:
        Set of generated words.
    """
    result = set()
    count = 0

    # Limit combinations to prevent infinite runtime
    digits_list = list(itertools.product(range(10), repeat=digit_length))

    for word in base_words:
        for digits_tuple in digits_list:
            if count >= max_permutations:
                return result

            digit_str = "".join(map(str, digits_tuple))
            for sep in separators:
                new_word = f"{word}{sep}{digit_str}"
                result.add(new_word)
                count += 1
                if count >= max_permutations:
                    return result

    return result
