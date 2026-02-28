"""Tests for configuration module."""

import pytest
from pathlib import Path

from password_generator.config import (
    PasswordSettings,
    Profile,
    get_settings,
    ConfigManager,
)


class TestProfile:
    """Tests for profile enum."""
    
    def test_profile_values(self):
        assert Profile.FAST.value == "fast"
        assert Profile.SECURE.value == "secure"
        assert Profile.PARANOID.value == "paranoid"
        assert Profile.CUSTOM.value == "custom"


class TestPasswordSettings:
    """Tests for settings class."""
    
    def test_default_settings(self):
        settings = PasswordSettings()
        assert settings.profile == Profile.SECURE
        assert settings.generator.length == 16
        assert settings.generator.use_uppercase is True
    
    def test_fast_profile(self):
        settings = PasswordSettings.from_profile(Profile.FAST)
        assert settings.profile == Profile.FAST
        assert settings.generator.length == 12
        assert settings.generator.use_special is False
    
    def test_paranoid_profile(self):
        settings = PasswordSettings.from_profile(Profile.PARANOID)
        assert settings.profile == Profile.PARANOID
        assert settings.generator.length == 32
        assert settings.generator.use_extended is True
    
    def test_profile_presets_fast(self):
        settings = PasswordSettings.from_profile(Profile.FAST)
        assert settings.performance.max_concurrent == 20
        assert settings.performance.show_progress is False
    
    def test_profile_presets_paranoid(self):
        settings = PasswordSettings.from_profile(Profile.PARANOID)
        assert settings.security.min_strength_score == 90
        assert settings.security.max_repeated_chars == 1


class TestConfigManager:
    """Tests for config manager."""
    
    def test_ensure_config_dir_creates_directory(self, tmp_path):
        config_path = tmp_path / "test_config.toml"
        manager = ConfigManager(config_path)
        manager.ensure_config_dir()
        assert config_path.parent.exists()
    
    def test_create_default_creates_file(self, tmp_path):
        config_path = tmp_path / "test_config.toml"
        manager = ConfigManager(config_path)
        path = manager.create_default(Profile.SECURE)
        
        assert path.exists()
        content = path.read_text()
        assert "profile" in content
    
    def test_load_nonexistent_returns_defaults(self, tmp_path):
        config_path = tmp_path / "nonexistent.toml"
        manager = ConfigManager(config_path)
        settings = manager.load()
        
        assert settings.profile == Profile.SECURE
    
    def test_save_and_load(self, tmp_path):
        config_path = tmp_path / "test_config.toml"
        manager = ConfigManager(config_path)
        
        settings = PasswordSettings.from_profile(Profile.FAST)
        manager.save(settings)
        
        loaded = manager.load()
        assert loaded.profile == Profile.FAST
    
    def test_get_config_info(self, tmp_path):
        config_path = tmp_path / "test_config.toml"
        manager = ConfigManager(config_path)
        
        info = manager.get_config_info()
        assert info["path"] == str(config_path)
        assert info["exists"] is False
        assert info["readable"] is False
        
        # Create file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("")
        
        info = manager.get_config_info()
        assert info["exists"] is True
        assert info["readable"] is True


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_get_settings_returns_instance(self):
        settings = get_settings()
        assert isinstance(settings, PasswordSettings)
    
    def test_get_settings_with_profile(self):
        settings = get_settings(Profile.FAST)
        assert settings.profile == Profile.FAST
    
    def test_get_settings_caches_result(self):
        settings1 = get_settings()
        settings2 = get_settings()
        # Should return same instance due to global caching
        assert settings1 is settings2
    
    def test_get_settings_reload(self):
        settings1 = get_settings(Profile.SECURE)
        settings2 = get_settings(Profile.FAST, reload=True)
        
        assert settings1.profile == Profile.SECURE
        assert settings2.profile == Profile.FAST
