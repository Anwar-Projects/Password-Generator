"""Password strength validation and scoring."""

from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional

from .entropy import calculate_entropy, analyze_patterns


class StrengthLevel(Enum):
    """Password strength levels."""
    CRITICAL = "critical"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    EXCELLENT = "excellent"


@dataclass
class StrengthScore:
    """Comprehensive password strength score."""
    score: int  # 0-100
    level: StrengthLevel
    entropy: float
    length: int
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_special: bool
    has_repeated: bool
    has_patterns: bool
    suggestions: list[str]
    passed_checks: list[str]
    failed_checks: list[str]


class PasswordValidator:
    """Validate and score password strength."""
    
    MIN_LENGTH = 8
    RECOMMENDED_LENGTH = 12
    EXCELLENT_LENGTH = 16
    
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "letmein", "dragon", "111111", "baseball",
        "iloveyou", "trustno1", "sunshine", "princess", "admin",
        "welcome", "shadow", "ashley", "football", "jesus",
        "michael", "ninja", "mustang", "password1", "123456789",
        "adobe123", "admin123", "letmein1", "photoshop", "1234567",
    }
    
    def __init__(
        self,
        min_length: int = MIN_LENGTH,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = False,
        max_repeated: int = 2,
        check_common: bool = True,
    ):
        """Initialize validator with custom rules.
        
        Args:
            min_length: Minimum password length.
            require_uppercase: Require uppercase letters.
            require_lowercase: Require lowercase letters.
            require_digits: Require digit characters.
            require_special: Require special characters.
            max_repeated: Maximum allowed consecutive repeated characters.
            check_common: Check against common passwords.
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.max_repeated = max_repeated
        self.check_common = check_common
    
    def validate(self, password: str) -> StrengthScore:
        """Validate and score a password.
        
        Args:
            password: The password to validate.
            
        Returns:
            StrengthScore with detailed analysis.
        """
        suggestions = []
        passed = []
        failed = []
        score = 0
        
        # Basic checks
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^*()_+\-=\[\]{}|;:,.?<>~`]', password))
        has_repeated = bool(re.search(rf'(.){{{self.max_repeated + 1},}}', password))
        
        # Length scoring
        length = len(password)
        if length >= self.EXCELLENT_LENGTH:
            score += 25
            passed.append("length_excellent")
        elif length >= self.RECOMMENDED_LENGTH:
            score += 15
            passed.append("length_good")
        elif length >= self.min_length:
            score += 10
            passed.append("length_minimum")
        else:
            failed.append("length")
            suggestions.append(f"Password should be at least {self.min_length} characters")
        
        # Character variety scoring
        if has_upper:
            score += 15
            passed.append("uppercase")
        elif self.require_uppercase:
            failed.append("uppercase")
            suggestions.append("Add uppercase letters")
            
        if has_lower:
            score += 15
            passed.append("lowercase")
        elif self.require_lowercase:
            failed.append("lowercase")
            suggestions.append("Add lowercase letters")
            
        if has_digit:
            score += 15
            passed.append("digits")
        elif self.require_digits:
            failed.append("digits")
            suggestions.append("Add numbers")
            
        if has_special:
            score += 20
            passed.append("special")
        elif self.require_special:
            failed.append("special")
            suggestions.append("Add special characters (!@#$%^*)")
        
        # Pattern analysis
        patterns = analyze_patterns(password)
        
        if has_repeated:
            score -= 10
            failed.append("repeated_chars")
            suggestions.append("Avoid repeating characters")
        else:
            passed.append("no_repeated")
            
        if patterns["is_predictable"]:
            score -= 15
            failed.append("patterns")
            suggestions.append("Avoid predictable patterns (keyboard walks, sequences)")
        else:
            passed.append("no_patterns")
        
        # Common password check
        if self.check_common and password.lower() in self.COMMON_PASSWORDS:
            score = 0
            failed.append("common_password")
            suggestions.append("This is a commonly used password - avoid it")
        else:
            passed.append("not_common")
        
        # Entropy bonus
        entropy_result = calculate_entropy(password)
        if entropy_result.category == "excellent":
            score += 10
        elif entropy_result.category == "very_strong":
            score += 5
            
        score = max(0, min(100, score))
        
        # Determine level
        if score < 20:
            level = StrengthLevel.CRITICAL
        elif score < 40:
            level = StrengthLevel.WEAK
        elif score < 60:
            level = StrengthLevel.MODERATE
        elif score < 75:
            level = StrengthLevel.STRONG
        elif score < 90:
            level = StrengthLevel.VERY_STRONG
        else:
            level = StrengthLevel.EXCELLENT
        
        if not suggestions:
            suggestions.append("Great password!")
            
        return StrengthScore(
            score=score,
            level=level,
            entropy=entropy_result.entropy,
            length=length,
            has_uppercase=has_upper,
            has_lowercase=has_lower,
            has_digits=has_digit,
            has_special=has_special,
            has_repeated=has_repeated,
            has_patterns=patterns["is_predictable"],
            suggestions=suggestions,
            passed_checks=passed,
            failed_checks=failed,
        )
    
    def is_strong_enough(self, password: str, min_score: int = 60) -> bool:
        """Quick check if password meets minimum strength.
        
        Args:
            password: The password to check.
            min_score: Minimum acceptable score.
            
        Returns:
            True if password is strong enough.
        """
        result = self.validate(password)
        return result.score >= min_score
