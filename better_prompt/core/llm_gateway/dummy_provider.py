"""
Dummy LLM Provider

A mock provider for testing and development purposes.
"""

from typing import List, Optional
import random

from .base import BaseLLMProvider, Message, LLMResponse, EmbeddingResponse


class DummyProvider(BaseLLMProvider):
    """
    Dummy LLM provider for testing.
    
    This provider returns mock responses without making actual API calls.
    Useful for development and testing.
    """
    
    MOCK_MODELS = [
        "dummy-gpt-4",
        "dummy-claude-3",
        "dummy-gemini-pro",
        "dummy-embedding-v1"
    ]
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the dummy provider.
        
        Args:
            api_key: Not required for dummy provider
            **kwargs: Additional configuration
        """
        super().__init__(api_key=api_key or "dummy-key", **kwargs)
        self.call_count = 0
    
    def completion(
        self,
        model: str,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a mock completion.
        
        Args:
            model: Model identifier
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse with mock content
        """
        self.call_count += 1
        
        # Generate mock response based on last user message
        user_messages = [m for m in messages if m.role.value == "user"]
        last_message = user_messages[-1].content if user_messages else "Hello"
        
        # Create a simple mock response
        mock_responses = [
            f"This is a mock response to: '{last_message[:50]}...'",
            f"I understand you asked about: {last_message[:30]}. Here's a dummy response.",
            f"Mock completion #{self.call_count} for your query.",
            "This is a simulated response from the dummy provider."
        ]
        
        content = random.choice(mock_responses)
        
        # Mock token usage
        prompt_tokens = sum(len(m.content.split()) for m in messages) * 2
        completion_tokens = len(content.split()) * 2
        
        return LLMResponse(
            content=content,
            model=model,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            metadata={
                "provider": "dummy",
                "call_count": self.call_count,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
    
    def embeddings(
        self,
        model: str,
        texts: List[str],
        **kwargs
    ) -> EmbeddingResponse:
        """
        Generate mock embeddings.
        
        Args:
            model: Embedding model identifier
            texts: List of texts to embed
            **kwargs: Additional parameters
            
        Returns:
            EmbeddingResponse with mock embedding vectors
        """
        self.call_count += 1
        
        # Generate random embeddings (dimension 1536 like OpenAI)
        embedding_dim = 1536
        embeddings = []
        
        for text in texts:
            # Use text length as seed for reproducibility
            random.seed(len(text))
            embedding = [random.random() for _ in range(embedding_dim)]
            embeddings.append(embedding)
        
        # Reset random seed
        random.seed()
        
        # Mock token usage
        total_tokens = sum(len(text.split()) for text in texts) * 2
        
        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage={
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
        )
    
    def list_models(self) -> List[str]:
        """
        List available mock models.
        
        Returns:
            List of mock model identifiers
        """
        return self.MOCK_MODELS.copy()
    
    def validate_connection(self) -> bool:
        """
        Always returns True for dummy provider.
        
        Returns:
            True
        """
        return True
    
    def reset_call_count(self) -> None:
        """Reset the call counter."""
        self.call_count = 0
    
    def get_call_count(self) -> int:
        """
        Get the number of API calls made.
        
        Returns:
            Number of calls
        """
        return self.call_count


# Register the dummy provider
from .base import LLMProviderFactory
LLMProviderFactory.register_provider("dummy", DummyProvider)
