"""Password Generator - A professional password generation tool.

This package provides advanced password generation capabilities including:
- Async/concurrent generation
- Cryptographically secure randomness
- Entropy calculation and strength validation
- Diceware/XKCD-style passphrases
- Multiple output formats (JSON, CSV, Hash, QR)
- Plugin architecture
- Profile-based configuration
"""

__version__ = "2.0.0"
__author__ = "Password Generator Team"

# Core components
from .core import PasswordGenerator
from .transformers import (
    capitalize_first_letter,
    replace_chars,
    generate_numbered_words,
)
from .utils import check_cpu_usage, setup_logging, CpuMonitor

# Security features
from .security import (
    calculate_entropy,
    estimate_crack_time,
    PasswordValidator,
    StrengthScore,
    DicewareGenerator,
    SecureRandom,
)

# Async core
from .async_core import (
    AsyncPasswordGenerator,
    PasswordStream,
    BackpressureHandler,
    AsyncPasswordWriter,
)

# Configuration
from .config import (
    PasswordSettings,
    Profile,
    get_settings,
    ConfigManager,
)

# Formats
from .formats import (
    OutputFormatter,
    PasswordRecord,
    get_formatter,
    list_formatters,
)

# Plugins
from .plugins import (
    GeneratorPlugin,
    TransformerPlugin,
    OutputPlugin,
    PluginRegistry,
)

__all__ = [
    # Core
    "PasswordGenerator",
    "capitalize_first_letter",
    "replace_chars",
    "generate_numbered_words",
    "check_cpu_usage",
    "setup_logging",
    "CpuMonitor",
    # Security
    "calculate_entropy",
    "estimate_crack_time",
    "PasswordValidator",
    "StrengthScore",
    "DicewareGenerator",
    "SecureRandom",
    # Async
    "AsyncPasswordGenerator",
    "PasswordStream",
    "BackpressureHandler",
    "AsyncPasswordWriter",
    # Configuration
    "PasswordSettings",
    "Profile",
    "get_settings",
    "ConfigManager",
    # Formats
    "OutputFormatter",
    "PasswordRecord",
    "get_formatter",
    "list_formatters",
    # Plugins
    "GeneratorPlugin",
    "TransformerPlugin",
    "OutputPlugin",
    "PluginRegistry",
]
