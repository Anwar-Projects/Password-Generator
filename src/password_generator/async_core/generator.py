"""Async password generator with concurrent streams."""

import asyncio
from typing import AsyncIterator, Callable, Optional
import string

from ..security.secrets_wrapper import SecureRandom
from ..security.diceware import DicewareGenerator


class AsyncPasswordGenerator:
    """Async password generator with backpressure handling."""
    
    def __init__(
        self,
        max_concurrent: int = 10,
        chunk_size: int = 100,
    ):
        """Initialize async generator.
        
        Args:
            max_concurrent: Maximum concurrent generation tasks.
            chunk_size: Size of chunks for batch generation.
        """
        self.max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._diceware = DicewareGenerator()
    
    async def generate_random_passwords(
        self,
        count: int,
        length: int = 16,
        alphabet: str | None = None,
    ) -> AsyncIterator[str]:
        """Generate random passwords asynchronously.
        
        Args:
            count: Number of passwords to generate.
            length: Length of each password.
            alphabet: Character set to use.
            
        Yields:
            Generated passwords.
        """
        chars = alphabet or (string.ascii_letters + string.digits + "!@#$%^*")
        
        for i in range(0, count, self.chunk_size):
            chunk = min(self.chunk_size, count - i)
            
            async with self._semaphore:
                tasks = [
                    asyncio.create_task(
                        self._generate_one(chars, length)
                    )
                    for _ in range(chunk)
                ]
                results = await asyncio.gather(*tasks)
                
                for password in results:
                    yield password
                    
                # Small delay to allow backpressure handling
                if i + chunk < count:
                    await asyncio.sleep(0.001)
    
    async def _generate_one(self, chars: str, length: int) -> str:
        """Generate a single password."""
        await asyncio.sleep(0)  # Yield control
        return SecureRandom.random_string(length, chars)
    
    async def generate_passphrases(
        self,
        count: int,
        word_count: int = 4,
        separator: str = "-",
    ) -> AsyncIterator[str]:
        """Generate diceware passphrases asynchronously.
        
        Args:
            count: Number of passphrases to generate.
            word_count: Words per passphrase.
            separator: Word separator.
            
        Yields:
            Generated passphrases.
        """
        for i in range(0, count, self.chunk_size):
            chunk = min(self.chunk_size, count - i)
            
            async with self._semaphore:
                passphrases = list(
                    self._diceware.generate(word_count, chunk)
                )
                
                for phrase in passphrases:
                    yield phrase
                    
                if i + chunk < count:
                    await asyncio.sleep(0.001)
    
    async def transform_stream(
        self,
        stream: AsyncIterator[str],
        transformer: Callable[[str], str],
        max_parallel: int = 5,
    ) -> AsyncIterator[str]:
        """Transform a password stream asynchronously.
        
        Args:
            stream: Input password stream.
            transformer: Transform function.
            max_parallel: Max parallel transforms.
            
        Yields:
            Transformed passwords.
        """
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def transform_one(password: str) -> str:
            async with semaphore:
                await asyncio.sleep(0)
                return transformer(password)
        
        tasks: list[asyncio.Task[str]] = []
        
        async for password in stream:
            if len(tasks) >= max_parallel:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in done:
                    yield await task
                tasks = list(pending)
            
            tasks.append(asyncio.create_task(transform_one(password)))
        
        if tasks:
            remaining = await asyncio.gather(*tasks)
            for result in remaining:
                yield result
    
    async def generate_variations(
        self,
        base_passwords: list[str],
        variations_per_password: int = 10,
    ) -> AsyncIterator[str]:
        """Generate password variations asynchronously.
        
        Args:
            base_passwords: Base passwords to vary.
            variations_per_password: Variations per base.
            
        Yields:
            Password variations.
        """
        leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
        
        async def vary_one(password: str) -> list[str]:
            await asyncio.sleep(0)
            variations = {password}
            
            # Leet speak variations
            leet = password.lower()
            for char, replacement in leet_map.items():
                leet = leet.replace(char, replacement)
            if leet != password.lower():
                variations.add(leet)
            
            # Capitalized variation
            variations.add(password.capitalize())
            
            # With trailing number
            variations.add(f"{password}{SecureRandom.randbelow(100)}")
            
            return list(variations)[:variations_per_password]
        
        tasks = [
            asyncio.create_task(vary_one(p))
            for p in base_passwords
        ]
        
        for task in asyncio.as_completed(tasks):
            variations = await task
            for v in variations:
                yield v
