"""Entropy calculation and password strength estimation."""

import math
import re
from typing import NamedTuple


class EntropyResult(NamedTuple):
    """Result of entropy calculation."""
    entropy: float
    pool_size: int
    character_count: int
    category: str


class CrackTimeResult(NamedTuple):
    """Result of crack time estimation."""
    seconds: float
    human_readable: str
    level: str


def calculate_pool_size(password: str) -> int:
    """Calculate the character pool size used in a password.
    
    Args:
        password: The password to analyze.
        
    Returns:
        Size of the character pool.
    """
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digits = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^*()_+\-=\[\]{}|;:,.?<>]', password))
    has_extended = bool(re.search(r'[^\x00-\x7F]', password))
    
    pool_size = 0
    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digits:
        pool_size += 10
    if has_special:
        pool_size += 23
    if has_extended:
        pool_size += 128
        
    return max(pool_size, 1)


def calculate_entropy(password: str) -> EntropyResult:
    """Calculate Shannon entropy of a password.
    
    Args:
        password: The password to analyze.
        
    Returns:
        EntropyResult with entropy bits and metadata.
    """
    pool_size = calculate_pool_size(password)
    length = len(password)
    
    if length == 0:
        return EntropyResult(0, pool_size, 0, "empty")
    
    # Shannon entropy calculation
    entropy = length * math.log2(pool_size)
    
    # Additional entropy for mixed case usage
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    if has_lower and has_upper:
        entropy += length * 0.5
    
    # Determine category
    if entropy < 28:
        category = "very_weak"
    elif entropy < 36:
        category = "weak"
    elif entropy < 60:
        category = "moderate"
    elif entropy < 80:
        category = "strong"
    elif entropy < 128:
        category = "very_strong"
    else:
        category = "excellent"
    
    return EntropyResult(
        entropy=round(entropy, 2),
        pool_size=pool_size,
        character_count=length,
        category=category
    )


def estimate_crack_time(
    password: str,
    guesses_per_second: float = 1e9
) -> CrackTimeResult:
    """Estimate time to crack password via brute force.
    
    Args:
        password: The password to analyze.
        guesses_per_second: Assumed attack speed (default: 1 billion/sec).
        
    Returns:
        CrackTimeResult with time estimates.
    """
    entropy_result = calculate_entropy(password)
    combinations = 2 ** entropy_result.entropy
    seconds = combinations / guesses_per_second
    
    if seconds < 1:
        human_readable = "instant"
        level = "critical"
    elif seconds < 60:
        human_readable = f"{int(seconds)} seconds"
        level = "critical"
    elif seconds < 3600:
        human_readable = f"{int(seconds / 60)} minutes"
        level = "critical"
    elif seconds < 86400:
        human_readable = f"{int(seconds / 3600)} hours"
        level = "weak"
    elif seconds < 2592000:
        human_readable = f"{int(seconds / 86400)} days"
        level = "weak"
    elif seconds < 31536000:
        human_readable = f"{int(seconds / 2592000)} months"
        level = "moderate"
    elif seconds < 315360000:
        human_readable = f"{int(seconds / 31536000)} years"
        level = "strong"
    elif seconds < 3153600000:
        human_readable = f"{int(seconds / 31536000)} decades"
        level = "very_strong"
    else:
        human_readable = "centuries"
        level = "excellent"
        
    return CrackTimeResult(
        seconds=round(seconds, 2),
        human_readable=human_readable,
        level=level
    )


def analyze_patterns(password: str) -> dict:
    """Analyze password for common weak patterns.
    
    Args:
        password: The password to analyze.
        
    Returns:
        Dictionary of detected patterns.
    """
    patterns = {
        "sequential_letters": bool(re.search(r'abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz', password.lower())),
        "sequential_numbers": bool(re.search(r'012|123|234|345|456|567|678|789|890', password)),
        "repeated_chars": bool(re.search(r'(.)\1{2,}', password)),
        "keyboard_patterns": bool(re.search(r'qwer|asdf|zxcv|1234|wasd', password.lower())),
        "date_patterns": bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}', password)),
        "common_substitutions": bool(re.search(r'[a@][s$5][o0]', password.lower())),
        "trailing_numbers": bool(re.search(r'.+\d{1,4}$', password)),
        "leading_capital": bool(re.search(r'^[A-Z][a-z]+$', password)),
    }
    
    patterns["risk_score"] = sum(1 for v in patterns.values() if v)
    patterns["is_predictable"] = patterns["risk_score"] >= 2
    
    return patterns
