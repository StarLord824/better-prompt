"""
LLM Gateway Base Module

This module provides abstract base classes for LLM provider interactions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


class MessageRole(Enum):
    """Message roles for chat-based models."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """
    A single message in a conversation.
    
    Attributes:
        role: The role of the message sender
        content: The message content
    """
    
    role: MessageRole
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format."""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass
class LLMResponse:
    """
    Response from an LLM provider.
    
    Attributes:
        content: The generated text content
        model: The model that generated the response
        usage: Token usage information
        metadata: Additional response metadata
    """
    
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Initialize optional fields."""
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class EmbeddingResponse:
    """
    Response from an embedding model.
    
    Attributes:
        embeddings: List of embedding vectors
        model: The model that generated the embeddings
        usage: Token usage information
    """
    
    embeddings: List[List[float]]
    model: str
    usage: Optional[Dict[str, int]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM provider implementations should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def completion(
        self,
        model: str,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion using the LLM.
        
        Args:
            model: Model identifier
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        pass
    
    @abstractmethod
    def embeddings(
        self,
        model: str,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """
        Generate embeddings for the given texts.
        
        Args:
            model: Embedding model identifier
            texts: List of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            EmbeddingResponse with embedding vectors
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of model identifiers
        """
        pass
    
    def validate_connection(self) -> bool:
        """
        Validate that the provider connection is working.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            models = self.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return self.__class__.__name__.replace("Provider", "")


class LLMProviderFactory:
    """
    Factory for creating LLM provider instances.
    """
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new provider class.
        
        Args:
            name: Provider name
            provider_class: Provider class (must inherit from BaseLLMProvider)
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError(
                f"Provider class must inherit from BaseLLMProvider, got {provider_class}"
            )
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def create_provider(cls, name: str, **kwargs) -> BaseLLMProvider:
        """
        Create a provider instance.
        
        Args:
            name: Provider name
            **kwargs: Provider configuration
            
        Returns:
            BaseLLMProvider instance
        """
        provider_class = cls._providers.get(name.lower())
        if not provider_class:
            raise ValueError(
                f"Unknown provider: {name}. Available providers: {list(cls._providers.keys())}"
            )
        return provider_class(**kwargs)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered providers.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
