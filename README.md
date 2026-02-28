# Password Generator

A professional, async password generation tool with advanced security features, multiple output formats, and a flexible plugin architecture.

## Features

- **Async/Concurrent Generation**: Non-blocking password generation with backpressure handling
- **Cryptographically Secure Randomness**: Uses Python's `secrets` module throughout
- **Entropy Calculation**: Calculate password entropy and estimate crack times
- **Strength Validation**: Comprehensive password strength scoring with suggestions
- **Diceware/XKCD Passphrases**: Generate memorable, high-entropy passphrases
- **Multiple Output Formats**: JSON, CSV, cryptographic hashes, QR codes
- **Plugin Architecture**: Extensible generator, transformer, and output plugins
- **Profile-Based Configuration**: Fast, Secure, Paranoid, and Custom profiles
- **TOML Configuration**: User-configurable settings via `~/.config/password-generator/config.toml`

## Installation

```bash
pip install password-generator
```

### From Source

```bash
git clone https://github.com/yourusername/password-generator.git
cd password-generator
pip install -e ".[dev]"
```

### Docker

```bash
docker build -t password-generator .
docker run password-generator --help
```

## Quick Start

```bash
# Generate 10 passwords
passgen --count 10 --output passwords.txt

# Generate with async CLI
passgen-async generate -n 100 -l 20 --entropy

# Generate diceware passphrase
passgen-async passphrase -n 5 -w 6

# Analyze password strength
passgen-async analyze --password "MyP@ssw0rd!"

# Generate XKCD-style passphrase
passgen-async passphrase --xkcd -n 3
```

## Usage

### CLI Commands

#### `passgen` (Traditional CLI)

```bash
# Basic generation
passgen --output passwords.txt

# Custom dictionary
passgen --dictionary "apple,banana,car" --output out.txt

# With seed for reproducibility
passgen --seed 42 --permutation-count 500

# CPU throttling
passgen --max-cpu 80
```

#### `passgen-async` (Modern Async CLI)

```bash
# Generate passwords with metadata
passgen-async generate -n 100 -o passwords.json -f json --entropy

# Password strength analysis
passgen-async analyze -p "TestPass123!"

# Analyze and output as JSON
passgen-async analyze -p "TestPass123!" --json

# Configuration management
passgen-async config
passgen-async config-init --profile secure
```

### Configuration Profiles

```bash
# Fast profile (quick, lower security)
passgen-async --profile fast generate -n 100

# Secure profile (balanced, default)
passgen-async --profile secure generate -n 50

# Paranoid profile (maximum security)
passgen-async --profile paranoid generate -n 10
```

### Configuration File

Create `~/.config/password-generator/config.toml`:

```toml
profile = "secure"

[generator]
length = 20
use_uppercase = true
use_lowercase = true
use_digits = true
use_special = true
min_entropy = 80.0

[passphrase]
word_count = 5
separator = "-"
capitalize = true

[security]
min_strength_score = 70
validate_patterns = true
check_common_passwords = true

[performance]
max_concurrent = 10
chunk_size = 100
show_progress = true
```

## API Usage

### Basic Generation

```python
from password_generator import PasswordGenerator

# Traditional synchronous generator
gen = PasswordGenerator()
passwords = gen.generate_passwords(
    include_permutations=True,
    enable_numbers=True,
)
print(f"Generated {len(passwords)} passwords")
```

### Async Generation

```python
import asyncio
from password_generator.async_core import AsyncPasswordGenerator

async def generate_passwords():
    gen = AsyncPasswordGenerator()
    
    async for password in gen.generate_random_passwords(100, length=20):
        print(password)

asyncio.run(generate_passwords())
```

### Secure Random Passwords

```python
from password_generator.security import SecureRandom

# Single password
password = SecureRandom.random_password(
    length=20,
    use_uppercase=True,
    use_lowercase=True,
    use_digits=True,
    use_special=True,
)
print(password)
```

### Passphrase Generation

```python
from password_generator.security import DicewareGenerator

# Diceware-style
generator = DicewareGenerator(separator="-")
for passphrase in generator.generate(word_count=6, num_passphrases=5):
    print(passphrase)

# XKCD-style (4 common words)
xkcd_passphrase = generator.generate_xkcd_style(4, " ")
print(xkcd_passphrase)
```

### Entropy Analysis

```python
from password_generator.security import calculate_entropy, estimate_crack_time

entropy_result = calculate_entropy("MyP@ssw0rd123!")
print(f"Entropy: {entropy_result.entropy} bits")
print(f"Category: {entropy_result.category}")

crack_time = estimate_crack_time("MyP@ssw0rd123!")
print(f"Estimated crack time: {crack_time.human_readable}")
```

### Password Validation

```python
from password_generator.security import PasswordValidator

validator = PasswordValidator()
score = validator.validate("MyP@ssw0rd123!")

print(f"Score: {score.score}/100")
print(f"Level: {score.level.value}")
print(f"Entropy: {score.entropy} bits")
print(f"Suggestions: {score.suggestions}")

# Quick check
if validator.is_strong_enough("MyP@ssw0rd123!"):
    print("Password is strong enough!")
```

### Custom Configuration

```python
from password_generator.config import PasswordSettings, Profile, get_settings

# Load default settings
settings = get_settings()

# Load from profile
secure_settings = get_settings(Profile.SECURE)
paranoid_settings = get_settings(Profile.PARANOID)

# Modify settings
settings.generator.length = 32
settings.security.min_strength_score = 90
```

### Output Formats

```python
from password_generator.formats import get_formatter, PasswordRecord
from datetime import datetime

# JSON output
formatter = get_formatter("json")
record = PasswordRecord(
    password="TestPass123!",
    timestamp=datetime.now().isoformat(),
    entropy=85.5,
    strength_score=75,
)
print(formatter.format_single(record))

# CSV output
formatter = get_formatter("csv")
print(formatter.format_single(record))

# Hash output
formatter = get_formatter("hash")
print(formatter.format_single(record))
```

### Plugin System

```python
from password_generator.plugins import GeneratorPlugin, PluginRegistry

class MyGenerator(GeneratorPlugin):
    name = "my_generator"
    description = "Custom password generator"
    
    def generate(self, count, **options):
        return ["custom_password"] * count
    
    def configure(self, **options):
        pass

# Register plugin
PluginRegistry.register_generator("my", MyGenerator)
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=password_generator --cov-report=html

# Run benchmarks
pytest tests/benchmarks/ --benchmark-only

# Run security checks
bandit -r src/password_generator
safety check
```

## Performance

### Benchmark Results

```bash
pytest tests/benchmarks/ --benchmark-only
```

Example benchmark output:
- Random password generation: ~0.05ms per password
- Entropy calculation: ~0.01ms per password
- Diceware passphrase generation: ~0.5ms per passphrase

### Async Performance

The async implementation provides significant performance improvements for large batches:

```python
# Async: ~10x faster for >1000 passwords
async_gen = AsyncPasswordGenerator()
async for pw in async_gen.generate_random_passwords(10000, 20):
    process(pw)
```

## Security Considerations

### Randomness Source

This package uses Python's `secrets` module for all cryptographic operations, which provides:
- Cryptographically strong random numbers
- Suitable for passwords, tokens, and security-sensitive operations
- Uses OS-provided entropy sources

### Password Strength

The strength validator checks for:
- Character variety (upper, lower, digits, special)
- No common/password list
- No sequential patterns
- No keyboard patterns
- Appropriate length

### Hash Algorithms

Supported hash output formats:
- `bcrypt` - Recommended for password storage
- `argon2` - Modern memory-hard hashing
- `scrypt` - Memory-hard key derivation
- `pbkdf2` - NIST-approved KDF
- `sha256/sha512` - For non-password use

**Note**: SHA-256/512 are not suitable for password storage

## Development

### Setup

```bash
pip install -e ".[dev,benchmark]"
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ tests/
ruff check --fix src/ tests/

# Type checking
mypy src/password_generator

# Security scan
bandit -r src/password_generator
```

## CI/CD

The project includes GitHub Actions workflows for:
- **CI**: Test on multiple Python versions and OS
- **Release**: Automatic PyPI and Docker Hub publishing
- **Security**: Bandit and Safety scans

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### v2.0.0
- Added async password generation
- Added configuration profiles (fast/secure/paranoid)
- Added TOML configuration support
- Added multiple output formats (JSON, CSV, Hash, QR)
- Added diceware/XKCD passphrase generation
- Added entropy and strength analysis
- Added plugin architecture
- Migrated to `secrets` module for cryptographic randomness
- Added comprehensive test suite
- Added Docker support
- Added CI/CD workflows
