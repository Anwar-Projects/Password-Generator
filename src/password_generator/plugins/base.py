"""Base plugin classes."""

from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar, Generic

T = TypeVar('T')


class GeneratorPlugin(ABC):
    """Base class for password generator plugins."""
    
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    
    @abstractmethod
    def generate(self, count: int, **options) -> list[str]:
        """Generate passwords.
        
        Args:
            count: Number of passwords to generate.
            **options: Generator options.
            
        Returns:
            List of generated passwords.
        """
        ...
    
    @abstractmethod
    def configure(self, **options) -> None:
        """Configure the generator."""
        ...


class TransformerPlugin(ABC):
    """Base class for password transformer plugins."""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    def transform(self, password: str, **options) -> str:
        """Transform a password.
        
        Args:
            password: Password to transform.
            **options: Transform options.
            
        Returns:
            Transformed password.
        """
        ...
    
    @abstractmethod
    def can_transform(self, password: str) -> bool:
        """Check if password can be transformed."""
        ...


class OutputPlugin(ABC):
    """Base class for output plugins."""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    def write(self, passwords: list[str], destination: str, **options) -> None:
        """Write passwords to destination.
        
        Args:
            passwords: Passwords to write.
            destination: Output destination.
            **options: Output options.
        """
        ...
    
    @abstractmethod
    def supports(self, destination: str) -> bool:
        """Check if destination is supported."""
        ...


class PluginRegistry:
    """Registry for plugins."""
    
    _generators: dict[str, type[GeneratorPlugin]] = {}
    _transformers: dict[str, type[TransformerPlugin]] = {}
    _outputs: dict[str, type[OutputPlugin]] = {}
    
    @classmethod
    def register_generator(cls, name: str, plugin_class: type[GeneratorPlugin]) -> None:
        """Register a generator plugin."""
        cls._generators[name] = plugin_class
    
    @classmethod
    def register_transformer(cls, name: str, plugin_class: type[TransformerPlugin]) -> None:
        """Register a transformer plugin."""
        cls._transformers[name] = plugin_class
    
    @classmethod
    def register_output(cls, name: str, plugin_class: type[OutputPlugin]) -> None:
        """Register an output plugin."""
        cls._outputs[name] = plugin_class
    
    @classmethod
    def get_generator(cls, name: str) -> type[GeneratorPlugin] | None:
        """Get generator plugin by name."""
        return cls._generators.get(name)
    
    @classmethod
    def get_transformer(cls, name: str) -> type[TransformerPlugin] | None:
        """Get transformer plugin by name."""
        return cls._transformers.get(name)
    
    @classmethod
    def get_output(cls, name: str) -> type[OutputPlugin] | None:
        """Get output plugin by name."""
        return cls._outputs.get(name)
    
    @classmethod
    def list_generators(cls) -> dict[str, type[GeneratorPlugin]]:
        """List registered generators."""
        return dict(cls._generators)
    
    @classmethod
    def list_transformers(cls) -> dict[str, type[TransformerPlugin]]:
        """List registered transformers."""
        return dict(cls._transformers)
    
    @classmethod
    def list_outputs(cls) -> dict[str, type[OutputPlugin]]:
        """List registered outputs."""
        return dict(cls._outputs)
