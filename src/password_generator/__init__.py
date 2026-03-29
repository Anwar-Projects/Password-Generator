"""Password Generator - A configurable password generation tool.

This module provides functionality to generate passwords with various
transformations and combinations.
"""

__version__ = "1.0.0"
__author__ = "Password Generator Team"

from .core import PasswordGenerator
from .transformers import (
    capitalize_first_letter,
    replace_chars,
    generate_numbered_words,
)
from .utils import check_cpu_usage, setup_logging

__all__ = [
    "PasswordGenerator",
    "capitalize_first_letter",
    "replace_chars",
    "generate_numbered_words",
    "check_cpu_usage",
    "setup_logging",
]
