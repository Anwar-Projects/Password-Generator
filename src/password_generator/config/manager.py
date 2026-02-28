"""Configuration file management."""

import shutil
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w

from .settings import PasswordSettings, Profile


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "password-generator" / "config.toml"


class ConfigManager:
    """Manage configuration files."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_path: Path to config file.
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        
    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
    def exists(self) -> bool:
        """Check if config file exists."""
        return self.config_path.exists()
    
    def load(self) -> PasswordSettings:
        """Load settings from TOML file.
        
        Returns:
            Loaded settings.
        """
        if not self.exists():
            return PasswordSettings()
            
        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)
            
        return PasswordSettings(**data)
    
    def save(self, settings: PasswordSettings) -> None:
        """Save settings to TOML file.
        
        Args:
            settings: Settings to save.
        """
        self.ensure_config_dir()
        
        data = {
            "profile": settings.profile.value,
            "generator": settings.generator.model_dump(),
            "passphrase": settings.passphrase.model_dump(),
            "output": settings.output.model_dump(),
            "security": settings.security.model_dump(),
            "performance": settings.performance.model_dump(),
        }
        
        with open(self.config_path, "wb") as f:
            tomli_w.dump(data, f)
    
    def create_default(self, profile: Profile = Profile.SECURE) -> Path:
        """Create default configuration file.
        
        Args:
            profile: Default profile to use.
            
        Returns:
            Path to created config.
        """
        self.ensure_config_dir()
        
        settings = PasswordSettings.from_profile(profile)
        self.save(settings)
        
        return self.config_path
    
    def migrate_config(self, old_path: Path, backup: bool = True) -> bool:
        """Migrate old configuration format.
        
        Args:
            old_path: Path to old config.
            backup: Create backup of old config.
            
        Returns:
            True if migration successful.
        """
        if not old_path.exists():
            return False
            
        try:
            # Create backup
            if backup:
                backup_path = old_path.with_suffix(".bak")
                shutil.copy2(old_path, backup_path)
                
            # Load and validate
            with open(old_path, "rb") as f:
                data = tomllib.load(f)
                
            settings = PasswordSettings(**data)
            self.save(settings)
            
            return True
        except Exception:
            return False
    
    def get_config_info(self) -> dict:
        """Get configuration information.
        
        Returns:
            Dict with config info.
        """
        info = {
            "path": str(self.config_path),
            "exists": self.exists(),
            "readable": False,
            "writable": False,
        }
        
        if self.exists():
            info["readable"] = self.config_path.is_file()
            info["writable"] = (
                self.config_path.stat().st_mode & 0o200
            ) != 0
            
        return info
