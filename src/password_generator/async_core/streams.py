"""Async stream handling with backpressure."""

import asyncio
from collections import deque
from typing import AsyncIterator, Callable, Optional, TypeVar

T = TypeVar('T')


class BackpressureHandler:
    """Handle backpressure for async streams."""
    
    def __init__(
        self,
        max_buffer_size: int = 1000,
        high_watermark: float = 0.8,
        low_watermark: float = 0.3,
    ):
        """Initialize backpressure handler.
        
        Args:
            max_buffer_size: Maximum items in buffer.
            high_watermark: Pause generation above this ratio.
            low_watermark: Resume generation below this ratio.
        """
        self.max_buffer_size = max_buffer_size
        self.high_watermark = int(max_buffer_size * high_watermark)
        self.low_watermark = int(max_buffer_size * low_watermark)
        self._buffer: deque[T] = deque()
        self._paused = False
        self._paused_event = asyncio.Event()
        self._paused_event.set()
    
    async def put(self, item: T) -> bool:
        """Add item to buffer with backpressure.
        
        Args:
            item: Item to add.
            
        Returns:
            True if added, False if buffer full.
        """
        if len(self._buffer) >= self.max_buffer_size:
            return False
            
        self._buffer.append(item)
        
        if len(self._buffer) >= self.high_watermark and not self._paused:
            self._paused = True
            self._paused_event.clear()
            
        return True
    
    def get(self) -> Optional[T]:
        """Get item from buffer.
        
        Returns:
            Item or None if empty.
        """
        if not self._buffer:
            return None
            
        item = self._buffer.popleft()
        
        if len(self._buffer) <= self.low_watermark and self._paused:
            self._paused = False
            self._paused_event.set()
            
        return item
    
    async def wait_if_paused(self) -> None:
        """Wait if generation is paused."""
        await self._paused_event.wait()
    
    def is_paused(self) -> bool:
        """Check if generation is paused."""
        return self._paused
    
    def size(self) -> int:
        """Get current buffer size."""
        return len(self._buffer)


class PasswordStream:
    """Async stream of passwords with backpressure."""
    
    def __init__(
        self,
        backpressure: Optional[BackpressureHandler] = None,
    ):
        """Initialize password stream.
        
        Args:
            backpressure: Backpressure handler.
        """
        self.backpressure = backpressure or BackpressureHandler()
        self._closed = False
        self._queue: asyncio.Queue[str] = asyncio.Queue()
    
    async def write(self, password: str) -> bool:
        """Write password to stream.
        
        Args:
            password: Password to write.
            
        Returns:
            True if written, False if stream closed.
        """
        if self._closed:
            return False
            
        await self.backpressure.wait_if_paused()
        
        if await self.backpressure.put(password):
            await self._queue.put(password)
            return True
        return False
    
    async def read(self) -> Optional[str]:
        """Read password from stream.
        
        Returns:
            Password or None if closed and empty.
        """
        if self._closed and self._queue.empty():
            return None
            
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
    
    async def __aiter__(self) -> AsyncIterator[str]:
        """Async iterator over stream."""
        while not self._closed or not self._queue.empty():
            password = await self.read()
            if password is None:
                break
            yield password
    
    def close(self) -> None:
        """Close the stream."""
        self._closed = True
    
    def is_closed(self) -> bool:
        """Check if stream is closed."""
        return self._closed
