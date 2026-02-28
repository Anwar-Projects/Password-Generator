"""Async file I/O for password generation."""

import asyncio
from pathlib import Path
from typing import AsyncIterator

import aiofiles


class AsyncPasswordWriter:
    """Async password file writer."""
    
    def __init__(
        self,
        output_path: str,
        mode: str = "a",
        encoding: str = "utf-8",
        buffer_size: int = 100,
    ):
        """Initialize async writer.
        
        Args:
            output_path: Output file path.
            mode: File open mode.
            encoding: Text encoding.
            buffer_size: Buffer before writing.
        """
        self.output_path = Path(output_path)
        self.mode = mode
        self.encoding = encoding
        self.buffer_size = buffer_size
        self._buffer: list[str] = []
        self._write_count = 0
        
    async def __aenter__(self) -> "AsyncPasswordWriter":
        """Enter async context."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = await aiofiles.open(
            self.output_path,
            mode=self.mode,
            encoding=self.encoding,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context, flush remaining."""
        await self.flush()
        await self._file.close()
    
    async def write(self, password: str) -> int:
        """Write password to buffer.
        
        Args:
            password: Password to write.
            
        Returns:
            Current buffer size.
        """
        self._buffer.append(password)
        self._write_count += 1
        
        if len(self._buffer) >= self.buffer_size:
            await self.flush()
            
        return len(self._buffer)
    
    async def writelines(self, passwords: list[str]) -> int:
        """Write multiple passwords.
        
        Args:
            passwords: Passwords to write.
            
        Returns:
            Total written.
        """
        self._buffer.extend(passwords)
        self._write_count += len(passwords)
        
        if len(self._buffer) >= self.buffer_size:
            await self.flush()
            
        return self._write_count
    
    async def flush(self) -> int:
        """Flush buffer to file.
        
        Returns:
            Number of items flushed.
        """
        if not self._buffer:
            return 0
            
        content = "\n".join(self._buffer) + "\n"
        await self._file.write(content)
        await self._file.flush()
        
        count = len(self._buffer)
        self._buffer.clear()
        return count
    
    async def write_stream(
        self,
        stream: AsyncIterator[str],
        progress_interval: int = 1000,
    ) -> int:
        """Write password stream to file.
        
        Args:
            stream: Async password stream.
            progress_interval: Report progress every N items.
            
        Returns:
            Total passwords written.
        """
        count = 0
        
        async for password in stream:
            await self.write(password)
            count += 1
            
            if count % progress_interval == 0:
                await self.flush()
        
        await self.flush()
        return count
    
    def get_count(self) -> int:
        """Get total write count."""
        return self._write_count
