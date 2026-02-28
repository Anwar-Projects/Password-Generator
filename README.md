# Password Generator

A configurable password generation tool with multiple transformation modes, CPU throttling, and CLI interface.

## Features

- **Multiple Transformations**: Capitalization, character replacement, random permutations
- **CLI Interface**: Full command-line interface with argparse
- **Type Hints**: Fully typed codebase
- **Performance Limits**: Built-in protections against runaway computation
- **CPU Monitoring**: Automatic throttling when CPU usage exceeds thresholds
- **Configurable**: Extensive options for customization

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Anwar-Projects/Password-Generator.git
cd Password-Generator

# Install with development dependencies
make install-dev
```

### Basic Install

```bash
pip install -e .
```

## Quick Start

```bash
# Generate passwords with default settings
passgen

# Generate with custom dictionary
passgen --dictionary "apple,banana,car"

# Generate with limited output
passgen --max-permutations 1000 --permutation-count 100

# Disable number suffixes
passgen --no-numbers --output simple_passwords.txt
```

## Usage

```
usage: passgen [-h] [-o OUTPUT] [-d DICTIONARY] [--dictionary-file DICTIONARY_FILE]
               [--max-permutations N] [--permutation-count N] [--permutation-length N]
               [--no-permutations] [--no-numbers] [--no-special-prefix] [--max-digit-length N]
               [--separators SEPARATORS] [--seed SEED] [--max-cpu PERCENT] [-v] [--version]

Generate password variations with multiple transformations.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (default: passwords.txt)
  -d DICTIONARY, --dictionary DICTIONARY
                        Comma-separated list of words (e.g., "apple,banana,car")
  --dictionary-file DICTIONARY_FILE
                        Path to file containing dictionary words (one per line)
  --max-permutations N  Maximum number of permutations to generate (default: 100000)
  --permutation-count N
                        Number of random permutations to generate (default: 1000)
  --permutation-length N
                        Length of random permutations (default: 4)
  --no-permutations     Skip random character permutations
  --no-numbers          Skip adding numerical suffixes
  --no-special-prefix   Skip adding "@" prefix with digits
  --max-digit-length N  Maximum number of digits for suffixes (default: 4)
  --separators SEPARATORS
                        Custom separator characters (default: special chars)
  --seed SEED           Random seed for reproducible output
  --max-cpu PERCENT     Maximum CPU usage before throttling (default: 80)
  -v, --verbose         Enable verbose logging
  --version             show program's version number and exit
```

## Development

### Setup

```bash
# Install development dependencies
make install-dev

# Or manually:
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_core.py
```

### Code Quality

```bash
# Run all linting
make lint

# Format code
make format

# Check formatting
make format-check

# Run type checking
make type-check
```

### Available Make Targets

| Target | Description |
|--------|-------------|
| `install` | Install the package |
| `install-dev` | Install with development dependencies |
| `test` | Run all tests |
| `test-cov` | Run tests with coverage |
| `lint` | Run all linting checks |
| `format` | Format code with black and ruff |
| `format-check` | Check code formatting |
| `type-check` | Run mypy type checking |
| `clean` | Remove build artifacts |
| `build` | Build the package |
| `run` | Run the password generator |

## How It Works

The generator applies transformations in sequence:

1. **Capitalized & Lowercase**: Dictionary words in both forms
2. **Random Permutations**: Random character combinations instead of exhaustive (prevents infinite runtime)
3. **Character Replacements**: a→@, o→0, i→1, s→5, etc.
4. **Numbered Variations**: Words with digit separators and suffixes
5. **Special Prefixes**: Words with @ prefix and digit suffix

## Configuration

### Dictionary File

Create a file with one word per line:

```
# words.txt
apple
banana
car
dog
```

Use with: `passgen --dictionary-file words.txt`

### Environment Variables

```bash
# Set default output file
export PASSGEN_OUTPUT=/path/to/passwords.txt

# Set CPU limit
export PASSGEN_MAX_CPU=70
```

## Architecture

```
.
├── src/
│   └── password_generator/
│       ├── __init__.py       # Package init
│       ├── cli.py            # Command-line interface
│       ├── core.py           # Core generation logic
│       ├── transformers.py   # Text transformation utilities
│       └── utils.py          # Logging and CPU monitoring
├── tests/
│   ├── test_cli.py
│   ├── test_core.py
│   └── test_transformers.py
├── pyproject.toml            # Package configuration
├── Makefile                # Build automation
└── README.md               # This file
```

## Why Not Exhaustive Permutations?

The original script attempted exhaustive permutations of 4-12 character alphabet combinations:

```python
# This creates astronomical numbers that never finish
itertools.permutations(alphabet, length)  # length 4-12
```

This version uses **random sampling** with configurable limits:

```python
# Fast and bounded
random.choices(alphabet, k=length)  # N random samples
```

For reference:
- 26P4 = 358,800
- 26P5 = 7,893,600
- 26P6 = 165,765,600
- 26P12 = ~10^14

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Run tests and linting (`make test lint`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing`)
6. Open a Pull Request
