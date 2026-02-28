"""Built-in transformer plugins."""

import re

from ..security.entropy import calculate_entropy
from ..security.validator import PasswordValidator, StrengthScore
from .base import TransformerPlugin


class LeetTransformer(TransformerPlugin):
    """Leetspeak transformation."""
    
    name = "leet"
    description = "Convert to leetspeak"
    
    LEET_MAP = {
        'a': '@', 'e': '3', 'i': '1', 'o': '0',
        's': '$', 't': '7', 'g': '9', 'b': '8',
    }
    
    def transform(self, password: str, **options) -> str:
        aggressive = options.get("aggressive", False)
        result = password.lower()
        
        for char, replacement in self.LEET_MAP.items():
            result = result.replace(char, replacement)
            
        if aggressive:
            # More aggressive substitutions
            result = result.replace('l', '1').replace('z', '2')
            
        return result
    
    def can_transform(self, password: str) -> bool:
        return any(c.lower() in self.LEET_MAP for c in password)


class SymbolTransformer(TransformerPlugin):
    """Symbol transformation."""
    
    name = "symbols"
    description = "Add decorative symbols"
    
    SYMBOLS = ["!", "@", "#", "$", "%", "^", "*", "&"]
    
    def transform(self, password: str, **options) -> str:
        position = options.get("position", "both")  # both, prefix, suffix
        count = options.get("count", 1)
        
        from ..security.secrets_wrapper import SecureRandom
        selected = ''.join(SecureRandom.choices(self.SYMBOLS, k=count))
        
        if position == "prefix":
            return selected + password
        elif position == "suffix":
            return password + selected
        else:  # both
            return selected + password + selected
    
    def can_transform(self, password: str) -> bool:
        return len(password) > 0


class CaseTransformer(TransformerPlugin):
    """Case transformation."""
    
    name = "case"
    description = "Transform letter case"
    
    def transform(self, password: str, **options) -> str:
        style = options.get("style", "random")
        
        if style == "upper":
            return password.upper()
        elif style == "lower":
            return password.lower()
        elif style == "capitalize":
            return password.capitalize()
        elif style == "alternating":
            return ''.join(
                c.upper() if i % 2 == 0 else c.lower()
                for i, c in enumerate(password)
            )
        elif style == "random":
            from ..security.secrets_wrapper import SecureRandom
            return ''.join(
                c.upper() if SecureRandom.randbelow(2) else c.lower()
                for c in password
            )
        return password
    
    def can_transform(self, password: str) -> bool:
        return bool(re.search(r'[a-zA-Z]', password))


class StrengthAnalyzer(TransformerPlugin):
    """Analyze password strength (pass-through with metadata)."""
    
    name = "strength"
    description = "Analyze and annotate password strength"
    
    def __init__(self):
        self._validator = PasswordValidator()
        self.last_analysis: StrengthScore | None = None
    
    def transform(self, password: str, **options) -> str:
        self.last_analysis = self._validator.validate(password)
        # Return password unchanged, analysis stored
        return password
    
    def can_transform(self, password: str) -> bool:
        return True
    
    def get_analysis(self) -> dict | None:
        """Get last analysis result."""
        if self.last_analysis:
            return {
                "score": self.last_analysis.score,
                "level": self.last_analysis.level.value,
                "entropy": self.last_analysis.entropy,
                "suggestions": self.last_analysis.suggestions,
            }
        return None
