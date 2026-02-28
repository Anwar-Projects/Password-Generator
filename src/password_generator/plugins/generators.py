"""Built-in generator plugins."""

from ..security.secrets_wrapper import SecureRandom
from ..security.diceware import DicewareGenerator
from .base import GeneratorPlugin


class RandomGenerator(GeneratorPlugin):
    """Generate random passwords."""
    
    name = "random"
    description = "Cryptographically secure random passwords"
    
    def __init__(self):
        self.length = 16
        self.use_upper = True
        self.use_lower = True
        self.use_digits = True
        self.use_special = True
    
    def configure(self, **options) -> None:
        self.length = options.get("length", 16)
        self.use_upper = options.get("use_uppercase", True)
        self.use_lower = options.get("use_lowercase", True)
        self.use_digits = options.get("use_digits", True)
        self.use_special = options.get("use_special", True)
    
    def generate(self, count: int, **options) -> list[str]:
        self.configure(**options)
        return [
            SecureRandom.random_password(
                self.length,
                self.use_upper,
                self.use_lower,
                self.use_digits,
                self.use_special,
            )
            for _ in range(count)
        ]


class PronounceableGenerator(GeneratorPlugin):
    """Generate pronounceable passwords."""
    
    name = "pronounceable"
    description = "Pronounceable/memorable passwords"
    
    VOWELS = "aeiou"
    CONSONANTS = "bcdfghjklmnpqrstvwxyz"
    
    def __init__(self):
        self.length = 10
        self.pattern = "CV"  # Consonant-Vowel pattern
    
    def configure(self, **options) -> None:
        self.length = options.get("length", 10)
        self.pattern = options.get("pattern", "CV")
    
    def generate(self, count: int, **options) -> list[str]:
        self.configure(**options)
        passwords = []
        
        for _ in range(count):
            pw = ""
            pattern_idx = 0
            
            while len(pw) < self.length:
                char_type = self.pattern[pattern_idx % len(self.pattern)]
                if char_type.upper() == "C":
                    pw += SecureRandom.choice(self.CONSONANTS)
                else:
                    pw += SecureRandom.choice(self.VOWELS)
                pattern_idx += 1
            
            # Capitalize first letter
            pw = pw[0].upper() + pw[1:] + str(SecureRandom.randbelow(100))
            passwords.append(pw)
            
        return passwords


class DicewareGeneratorPlugin(GeneratorPlugin):
    """Generate diceware passphrases."""
    
    name = "diceware"
    description = "Diceware-style passphrases"
    
    def __init__(self):
        self._generator = DicewareGenerator()
        self.word_count = 6
        self.separator = "-"
    
    def configure(self, **options) -> None:
        self.word_count = options.get("word_count", 6)
        self.separator = options.get("separator", "-")
    
    def generate(self, count: int, **options) -> list[str]:
        self.configure(**options)
        self._generator.separator = self.separator
        return list(self._generator.generate(self.word_count, count))


class XKCDGenerator(GeneratorPlugin):
    """Generate xkcd-style passphrases."""
    
    name = "xkcd"
    description = "XKCD-style memorable passphrases"
    
    def __init__(self):
        self._generator = DicewareGenerator()
    
    def configure(self, **options) -> None:
        self.word_count = options.get("word_count", 4)
        self.separator = options.get("separator", " ")
    
    def generate(self, count: int, **options) -> list[str]:
        self.configure(**options)
        return [
            self._generator.generate_xkcd_style(self.word_count, self.separator)
            for _ in range(count)
        ]
