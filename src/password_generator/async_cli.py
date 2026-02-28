"""Async command-line interface for password generator."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .async_core import AsyncPasswordGenerator, AsyncPasswordWriter, BackpressureHandler
from .config import get_settings, Profile, ConfigManager
from .formats import get_formatter, PasswordRecord
from .security import SecureRandom, PasswordValidator


console = Console()


@click.group()
@click.option(
    "--profile",
    type=click.Choice(["fast", "secure", "paranoid", "custom"]),
    default="secure",
    help="Configuration profile",
)
@click.option("--config", type=click.Path(), help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, profile: str, config: Optional[str]) -> None:
    """Async password generator CLI."""
    ctx.ensure_object(dict)
    
    # Load configuration
    if config:
        config_path = Path(config)
        if config_path.exists():
            settings = ConfigManager(config_path).load()
        else:
            console.print(f"[red]Config file not found: {config}[/red]")
            sys.exit(1)
    else:
        settings = get_settings(Profile(profile))
    
    ctx.obj["settings"] = settings
    ctx.obj["profile"] = profile


@cli.command()
@click.option("-n", "--count", default=10, help="Number of passwords to generate")
@click.option("-l", "--length", default=16, help="Password length")
@click.option("-o", "--output", default="passwords.txt", help="Output file")
@click.option("-f", "--format", "fmt", default="text", help="Output format")
@click.option("--async/--no-async", "is_async", default=True, help="Use async generation")
@click.option("--entropy", is_flag=True, help="Include entropy calculation")
@click.option("--validate", is_flag=True, help="Validate password strength")
@click.pass_context
def generate(
    ctx: click.Context,
    count: int,
    length: int,
    output: str,
    fmt: str,
    is_async: bool,
    entropy: bool,
    validate: bool,
) -> None:
    """Generate random passwords."""
    settings = ctx.obj["settings"]
    
    if is_async:
        asyncio.run(
            _async_generate(count, length, output, fmt, entropy, validate, settings)
        )
    else:
        _sync_generate(count, length, output, fmt, entropy, validate)


async def _async_generate(
    count: int,
    length: int,
    output: str,
    fmt: str,
    with_entropy: bool,
    validate: bool,
    settings,
) -> None:
    """Async generation implementation."""
    generator = AsyncPasswordGenerator(
        max_concurrent=settings.performance.max_concurrent,
        chunk_size=settings.performance.chunk_size,
    )
    
    validator = PasswordValidator() if validate else None
    records = []
    passwords = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Generating {count} passwords...", total=None)
        
        async for password in generator.generate_random_passwords(count, length):
            passwords.append(password)
            
            if with_entropy or validate:
                from .security.entropy import calculate_entropy, estimate_crack_time
                from datetime import datetime
                
                ent = calculate_entropy(password)
                crack = estimate_crack_time(password)
                
                record = PasswordRecord(
                    password=password,
                    timestamp=datetime.now().isoformat(),
                    entropy=ent.entropy,
                    strength_level=ent.category if validate else None,
                    crack_time=crack.human_readable if with_entropy else None,
                )
                
                if validate:
                    score = validator.validate(password)
                    record.strength_score = score.score
                    record.strength_level = score.level.value
                
                records.append(record)
            
            progress.advance(task)
        
        progress.update(task, completed=True, description="Generation complete!")
    
    # Output
    if fmt == "text":
        async with AsyncPasswordWriter(output) as writer:
            await writer.writelines(passwords)
    else:
        formatter = get_formatter(fmt)
        if formatter and records:
            content = formatter.format_batch(records)
            async with AsyncPasswordWriter(output) as writer:
                await writer._file.write(content)
    
    console.print(f"[green]✓[/green] Generated {count} passwords saved to {output}")


def _sync_generate(
    count: int,
    length: int,
    output: str,
    fmt: str,
    with_entropy: bool,
    validate: bool,
) -> None:
    """Sync generation implementation."""
    passwords = [
        SecureRandom.random_password(length)
        for _ in range(count)
    ]
    
    Path(output).write_text("\n".join(passwords) + "\n")
    console.print(f"[green]✓[/green] Generated {count} passwords saved to {output}")


@cli.command()
@click.option("-n", "--count", default=5, help="Number of passphrases")
@click.option("-w", "--words", default=4, help="Words per passphrase")
@click.option("-s", "--separator", default="-", help="Word separator")
@click.option("-o", "--output", default="passphrases.txt", help="Output file")
@click.option("--xkcd", is_flag=True, help="XKCD style (4 common words)")
@click.pass_context
def passphrase(
    ctx: click.Context,
    count: int,
    words: int,
    separator: str,
    output: str,
    xkcd: bool,
) -> None:
    """Generate diceware passphrases."""
    from .security.diceware import DicewareGenerator
    
    generator = DicewareGenerator(separator=separator)
    
    if xkcd:
        passphrases = [
            generator.generate_xkcd_style(words, separator)
            for _ in range(count)
        ]
    else:
        passphrases = list(generator.generate(words, count))
    
    Path(output).write_text("\n".join(passphrases) + "\n")
    console.print(f"[green]✓[/green] Generated {count} passphrases saved to {output}")


@cli.command()
@click.option("-p", "--password", required=True, help="Password to analyze")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def analyze(password: str, as_json: bool) -> None:
    """Analyze password strength and entropy."""
    from .security.entropy import calculate_entropy, estimate_crack_time
    import json as json_module
    
    entropy = calculate_entropy(password)
    crack = estimate_crack_time(password)
    validator = PasswordValidator()
    score = validator.validate(password)
    
    if as_json:
        result = {
            "password": password[:4] + "****",
            "entropy": entropy.entropy,
            "pool_size": entropy.pool_size,
            "category": entropy.category,
            "crack_time": crack.human_readable,
            "crack_level": crack.level,
            "strength_score": score.score,
            "strength_level": score.level.value,
            "suggestions": score.suggestions,
        }
        console.print(json_module.dumps(result, indent=2))
    else:
        console.print(f"\n[bold]Password Analysis[/bold]")
        console.print(f"Entropy: {entropy.entropy:.2f} bits ({entropy.category})")
        console.print(f"Estimated crack time: {crack.human_readable}")
        console.print(f"Strength Score: {score.score}/100 ({score.level.value})")
        
        if score.suggestions:
            console.print("\n[bold]Suggestions:[/bold]")
            for suggestion in score.suggestions:
                console.print(f"  • {suggestion}")


@cli.command(name="config")
def config_cmd() -> None:
    """Show configuration info."""
    manager = ConfigManager()
    info = manager.get_config_info()
    
    console.print("\n[bold]Configuration[/bold]")
    console.print(f"Path: {info['path']}")
    console.print(f"Exists: {info['exists']}")
    console.print(f"Readable: {info['readable']}")
    console.print(f"Writable: {info['writable']}")
    
    if not info['exists']:
        console.print("\n[italic]Run 'passgen-async config-init' to create default config[/italic]")


@cli.command(name="config-init")
@click.option("--profile", default="secure", help="Default profile")
def config_init(profile: str) -> None:
    """Initialize configuration file."""
    try:
        p = Profile(profile)
    except ValueError:
        console.print(f"[red]Invalid profile: {profile}[/red]")
        sys.exit(1)
    
    manager = ConfigManager()
    path = manager.create_default(p)
    console.print(f"[green]✓[/green] Created config at {path}")


def main() -> int:
    """Main entry point."""
    try:
        cli()
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
