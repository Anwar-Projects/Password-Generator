"""Pydantic settings for password generation."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Profile(str, Enum):
    """Predefined configuration profiles."""
    FAST = "fast"
    SECURE = "secure"
    PARANOID = "paranoid"
    CUSTOM = "custom"


class GeneratorConfig(BaseModel):
    """Generator configuration."""
    length: int = Field(default=16, ge=4, le=256)
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_special: bool = True
    use_extended: bool = False
    min_entropy: float = Field(default=50.0, ge=0)
    avoid_ambiguous: bool = True
    require_all_charsets: bool = True


class PassphraseConfig(BaseModel):
    """Passphrase generation configuration."""
    word_count: int = Field(default=4, ge=2, le=20)
    wordlist_path: Optional[str] = None
    separator: str = "-"
    capitalize: bool = False
    append_number: bool = False
    min_word_length: int = 3
    max_word_length: int = 8


class OutputConfig(BaseModel):
    """Output configuration."""
    format: str = "text"
    include_metadata: bool = False
    include_entropy: bool = False
    hash_algorithms: list[str] = Field(default_factory=lambda: ["bcrypt"])
    output_path: Optional[str] = None
    overwrite: bool = False
    append: bool = False


class SecurityConfig(BaseModel):
    """Security configuration."""
    min_strength_score: int = Field(default=60, ge=0, le=100)
    validate_patterns: bool = True
    check_common_passwords: bool = True
    max_repeated_chars: int = Field(default=2, ge=1)
    require_unique_passwords: bool = True


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    max_concurrent: int = Field(default=10, ge=1, le=100)
    chunk_size: int = Field(default=100, ge=10, le=10000)
    buffer_size: int = Field(default=1000, ge=100, le=100000)
    use_async: bool = True
    show_progress: bool = True


class ProfilePresets:
    """Profile preset configurations."""
    
    @staticmethod
    def fast() -> dict:
        """Fast generation profile."""
        return {
            "generator": {
                "length": 12,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_digits": True,
                "use_special": False,
                "min_entropy": 40.0,
                "avoid_ambiguous": True,
                "require_all_charsets": False,
            },
            "passphrase": {
                "word_count": 3,
                "separator": "-",
                "capitalize": False,
            },
            "security": {
                "min_strength_score": 40,
                "validate_patterns": False,
                "check_common_passwords": True,
            },
            "performance": {
                "max_concurrent": 20,
                "chunk_size": 500,
                "use_async": True,
                "show_progress": False,
            },
        }
    
    @staticmethod
    def secure() -> dict:
        """Secure generation profile."""
        return {
            "generator": {
                "length": 20,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_digits": True,
                "use_special": True,
                "min_entropy": 80.0,
                "avoid_ambiguous": True,
                "require_all_charsets": True,
            },
            "passphrase": {
                "word_count": 5,
                "separator": "-",
                "capitalize": True,
                "append_number": True,
            },
            "security": {
                "min_strength_score": 70,
                "validate_patterns": True,
                "check_common_passwords": True,
                "max_repeated_chars": 2,
            },
            "performance": {
                "max_concurrent": 10,
                "chunk_size": 100,
                "use_async": True,
                "show_progress": True,
            },
        }
    
    @staticmethod
    def paranoid() -> dict:
        """Maximum security profile."""
        return {
            "generator": {
                "length": 32,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_digits": True,
                "use_special": True,
                "use_extended": True,
                "min_entropy": 128.0,
                "avoid_ambiguous": False,
                "require_all_charsets": True,
            },
            "passphrase": {
                "word_count": 8,
                "separator": " ",
                "capitalize": True,
                "append_number": True,
            },
            "security": {
                "min_strength_score": 90,
                "validate_patterns": True,
                "check_common_passwords": True,
                "max_repeated_chars": 1,
                "require_unique_passwords": True,
            },
            "performance": {
                "max_concurrent": 5,
                "chunk_size": 50,
                "use_async": True,
                "show_progress": True,
            },
        }


class PasswordSettings(BaseSettings):
    """Complete password generator settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="PASSGEN_",
        toml_file=["~/.config/password-generator/config.toml", ".passgen.toml"],
        extra="ignore",
    )
    
    profile: Profile = Field(default=Profile.SECURE)
    generator: GeneratorConfig = Field(default_factory=GeneratorConfig)
    passphrase: PassphraseConfig = Field(default_factory=PassphraseConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    @classmethod
    def from_profile(cls, profile: Profile) -> "PasswordSettings":
        """Create settings from profile preset.
        
        Args:
            profile: Profile to use.
            
        Returns:
            Configured settings.
        """
        if profile == Profile.FAST:
            data = ProfilePresets.fast()
        elif profile == Profile.SECURE:
            data = ProfilePresets.secure()
        elif profile == Profile.PARANOID:
            data = ProfilePresets.paranoid()
        else:
            return cls()
            
        return cls(profile=profile, **data)
    
    @field_validator("profile", mode="before")
    @classmethod
    def validate_profile(cls, v) -> Profile:
        """Validate profile value."""
        if isinstance(v, str):
            return Profile(v.lower())
        return v


# Global settings instance
_settings: Optional[PasswordSettings] = None


def get_settings(
    profile: Optional[Profile] = None,
    reload: bool = False,
) -> PasswordSettings:
    """Get global settings instance.
    
    Args:
        profile: Optional profile to load.
        reload: Force reload from file.
        
    Returns:
        Settings instance.
    """
    global _settings
    
    if _settings is None or reload:
        if profile:
            _settings = PasswordSettings.from_profile(profile)
        else:
            _settings = PasswordSettings()
            
    return _settings
