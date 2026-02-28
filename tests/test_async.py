"""Tests for async functionality."""

import asyncio
import pytest

from password_generator.async_core import (
    AsyncPasswordGenerator,
    AsyncPasswordWriter,
    BackpressureHandler,
    PasswordStream,
)


@pytest.mark.asyncio
class TestAsyncPasswordGenerator:
    """Tests for async generator."""
    
    async def test_generate_random_passwords(self, tmp_path):
        generator = AsyncPasswordGenerator()
        passwords = []
        
        async for pw in generator.generate_random_passwords(10, 12):
            passwords.append(pw)
            assert len(pw) == 12
        
        assert len(passwords) == 10
        assert len(set(passwords)) == 10  # All unique
    
    async def test_generate_passphrases(self):
        generator = AsyncPasswordGenerator()
        passphrases = []
        
        async for phrase in generator.generate_passphrases(5, 4):
            passphrases.append(phrase)
            words = phrase.split("-")
            assert len(words) == 4
        
        assert len(passphrases) == 5
    
    async def test_transform_stream(self):
        generator = AsyncPasswordGenerator()
        
        async def source():
            for i in range(5):
                yield f"test{i}"
        
        transformed = []
        async for pw in generator.transform_stream(
            source(), lambda x: x.upper(), max_parallel=2
        ):
            transformed.append(pw)
            assert pw.startswith("TEST")
        
        assert len(transformed) == 5
    
    async def test_generate_variations(self):
        generator = AsyncPasswordGenerator()
        variations = []
        
        async for v in generator.generate_variations(["password"], 5):
            variations.append(v)
        
        assert len(variations) > 0


@pytest.mark.asyncio
class TestBackpressureHandler:
    """Tests for backpressure handling."""
    
    async def test_put_adds_items(self):
        handler = BackpressureHandler(max_buffer_size=10)
        
        for i in range(5):
            result = await handler.put(f"item{i}")
            assert result is True
        
        assert handler.size() == 5
    
    async def test_put_returns_false_when_full(self):
        handler = BackpressureHandler(max_buffer_size=5)
        
        for i in range(5):
            await handler.put(f"item{i}")
        
        result = await handler.put("overflow")
        assert result is False
    
    async def test_get_removes_items(self):
        handler = BackpressureHandler()
        await handler.put("item1")
        await handler.put("item2")
        
        item = handler.get()
        assert item == "item1"
        assert handler.size() == 1
    
    async def test_pause_at_high_watermark(self):
        handler = BackpressureHandler(
            max_buffer_size=100,
            high_watermark=0.5,
            low_watermark=0.3
        )
        
        # Fill to above high watermark
        for i in range(60):
            await handler.put(f"item{i}")
        
        assert handler.is_paused()
    
    async def test_resume_at_low_watermark(self):
        handler = BackpressureHandler(
            max_buffer_size=100,
            high_watermark=0.5,
            low_watermark=0.3
        )
        
        # Fill and drain
        for i in range(60):
            await handler.put(f"item{i}")
        
        assert handler.is_paused()
        
        # Drain below low watermark
        for _ in range(40):
            handler.get()
        
        # Should still be paused (need one more to hit 30)
        assert handler.is_paused()
        
        handler.get()
        assert not handler.is_paused()


@pytest.mark.asyncio
class TestAsyncPasswordWriter:
    """Tests for async file writer."""
    
    async def test_write_creates_file(self, tmp_path):
        output_file = tmp_path / "test.txt"
        
        async with AsyncPasswordWriter(str(output_file)) as writer:
            await writer.write("password1")
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "password1" in content
    
    async def test_writelines_writes_multiple(self, tmp_path):
        output_file = tmp_path / "test.txt"
        
        async with AsyncPasswordWriter(str(output_file)) as writer:
            await writer.writelines(["pw1", "pw2", "pw3"])
        
        content = output_file.read_text().strip()
        assert content == "pw1\npw2\npw3"
    
    async def test_write_stream(self, tmp_path):
        output_file = tmp_path / "test.txt"
        
        async def source():
            for i in range(5):
                yield f"password{i}"
        
        async with AsyncPasswordWriter(str(output_file)) as writer:
            count = await writer.write_stream(source())
        
        assert count == 5
        content = output_file.read_text().strip().split("\n")
        assert len(content) == 5


@pytest.mark.asyncio
class TestPasswordStream:
    """Tests for password stream."""
    
    async def test_write_and_read(self):
        stream = PasswordStream()
        
        await stream.write("password1")
        await stream.write("password2")
        
        pw1 = await stream.read()
        pw2 = await stream.read()
        
        assert pw1 == "password1"
        assert pw2 == "password2"
    
    async def test_stream_iteration(self):
        stream = PasswordStream()
        
        await stream.write("pw1")
        await stream.write("pw2")
        stream.close()
        
        passwords = []
        async for pw in stream:
            passwords.append(pw)
        
        assert "pw1" in passwords
        assert "pw2" in passwords
    
    async def test_closed_stream_returns_none(self):
        stream = PasswordStream()
        stream.close()
        
        result = await stream.read()
        assert result is None
