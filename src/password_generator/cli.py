"""Command-line interface for password generator."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .core import PasswordGenerator
from .utils import setup_logging, CpuMonitor


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="passgen",
        description="Generate password variations with multiple transformations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  passgen --output passwords.txt
  passgen --dictionary "word1,word2,word3" --output out.txt
  passgen --max-permutations 1000 --no-numbers
  passgen --seed 42 --permutation-count 500
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="passwords.txt",
        help="Output file path (default: passwords.txt)",
    )

    parser.add_argument(
        "-d",
        "--dictionary",
        type=str,
        help='Comma-separated list of words (e.g., "apple,banana,car")',
    )

    parser.add_argument(
        "--dictionary-file",
        type=str,
        help="Path to file containing dictionary words (one per line)",
    )

    parser.add_argument(
        "--max-permutations",
        type=int,
        default=100_000,
        metavar="N",
        help="Maximum number of permutations to generate (default: 100000)",
    )

    parser.add_argument(
        "--permutation-count",
        type=int,
        default=1000,
        metavar="N",
        help="Number of random permutations to generate (default: 1000)",
    )

    parser.add_argument(
        "--permutation-length",
        type=int,
        default=4,
        metavar="N",
        help="Length of random permutations (default: 4)",
    )

    parser.add_argument(
        "--no-permutations",
        action="store_true",
        help="Skip random character permutations",
    )

    parser.add_argument(
        "--no-numbers",
        action="store_true",
        help="Skip adding numerical suffixes",
    )

    parser.add_argument(
        "--no-special-prefix",
        action="store_true",
        help='Skip adding "@" prefix with digits',
    )

    parser.add_argument(
        "--max-digit-length",
        type=int,
        default=4,
        metavar="N",
        help="Maximum number of digits for suffixes (default: 4)",
    )

    parser.add_argument(
        "--separators",
        type=str,
        default=None,
        help='Custom separator characters (default: special chars)',
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output",
    )

    parser.add_argument(
        "--max-cpu",
        type=float,
        default=80.0,
        metavar="PERCENT",
        help="Maximum CPU usage before throttling (default: 80)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


def load_dictionary(dictionary_arg: Optional[str], dictionary_file: Optional[str]) -> list[str]:
    """Load dictionary words from arguments or file.

    Args:
        dictionary_arg: Comma-separated words.
        dictionary_file: Path to dictionary file.

    Returns:
        List of dictionary words.
    """
    if dictionary_arg:
        return [w.strip() for w in dictionary_arg.split(",") if w.strip()]

    if dictionary_file:
        path = Path(dictionary_file)
        if not path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {dictionary_file}")
        return [
            line.strip()
            for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]

    return []  # Use defaults


def write_passwords(passwords: set[str], output_path: str) -> int:
    """Write passwords to file.

    Args:
        passwords: Set of generated passwords.
        output_path: Output file path.

    Returns:
        Number of passwords written.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        for pwd in sorted(passwords):
            f.write(f"{pwd}\\n")

    return len(passwords)


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Setup logging
    log_level = logging.DEBUG if parsed.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting password generation...")

    try:
        # Load dictionary
        dictionary = load_dictionary(parsed.dictionary, parsed.dictionary_file)
        if dictionary:
            logger.info(f"Loaded {len(dictionary)} dictionary words")

        # Create generator
        generator = PasswordGenerator(
            dictionary=dictionary if dictionary else None,
            max_permutations=parsed.max_permutations,
            seed=parsed.seed,
        )

        # Throttle if needed
        with CpuMonitor(max_percent=parsed.max_cpu) as monitor:
            monitor.throttle_if_needed()

            # Generate passwords
            logger.info("Generating passwords...")
            passwords = generator.generate_passwords(
                include_permutations=not parsed.no_permutations,
                permutation_length=parsed.permutation_length,
                permutation_count=parsed.permutation_count,
                enable_numbers=not parsed.no_numbers,
                enable_special_prefix=not parsed.no_special_prefix,
                max_digit_length=parsed.max_digit_length,
            )

            monitor.throttle_if_needed()

        # Write output
        count = write_passwords(passwords, parsed.output)
        logger.info(f"Generated {count} passwords written to {parsed.output}")
        print(f"\\n✓ Generated {count} passwords written to: {parsed.output}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user")
        print("\\nOperation cancelled.", file=sys.stderr)
        return 130

    except Exception as e:
        logger.exception("Unexpected error")
        print(f"\\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
