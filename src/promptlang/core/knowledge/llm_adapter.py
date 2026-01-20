"""
LLM Client Adapter for Option C (Hybrid RAG + LLM Refinement)

This adapter wraps the PromptLang LLMProviderManager to provide the interface
expected by the KnowledgeRetriever's LLM refinement functionality.
"""

from typing import Any


class MockResponse:
    """Mock OpenAI-like response object."""
    
    def __init__(self, content: str):
        self.content = content
    
    class choices:
        """Mock choices container."""
        
        def __init__(self, content: str):
            self.content = content
        
        def __getitem__(self, _):
            """Return a mock choice."""
            class MockChoice:
                def __init__(self, content: str):
                    self.content = content
                
                class message:
                    """Mock message container."""
                    def __init__(self, content: str):
                        self.content = content
                
                def __init__(self, content: str):
                    self.message = self.message(content)
            
            return MockChoice(self.content)


class LLMClientAdapter:
    """Adapter to make LLMProviderManager compatible with LLM refinement interface."""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
    
    class chat:
        """Nested chat class to match OpenAI-like interface."""
        
        def __init__(self, llm_manager):
            self.llm_manager = llm_manager
        
        class completions:
            """Nested completions class to match OpenAI-like interface."""
            
            def __init__(self, llm_manager):
                self.llm_manager = llm_manager
            
            async def create(self, *args, **kwargs) -> Any:
                """Create a completion using the LLM manager."""
                # Extract messages from kwargs
                messages = kwargs.get('messages', [])
                temperature = kwargs.get('temperature', 0.1)
                max_tokens = kwargs.get('max_tokens', 200)
                
                # Convert messages to prompt format
                system_prompt = ""
                user_prompt = ""
                
                for msg in messages:
                    if msg.get('role') == 'system':
                        system_prompt = msg.get('content', '')
                    elif msg.get('role') == 'user':
                        user_prompt = msg.get('content', '')
                
                # Get the llm_manager from the parent
                llm_manager = self.llm_manager
                
                if not llm_manager:
                    # Fallback response
                    return MockResponse("[1, 2, 3]")
                
                # Generate response using LLM manager
                try:
                    response = await llm_manager.generate_with_fallback(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    # Create OpenAI-like response object
                    return MockResponse(response.content)
                    
                except Exception as e:
                    print(f"LLM generation failed: {e}")
                    # Fallback response
                    return MockResponse("[1, 2, 3]")


def create_llm_adapter(llm_manager) -> Any:
    """Create an LLM client adapter for the given LLM manager.
    
    Args:
        llm_manager: LLMProviderManager instance
        
    Returns:
        Adapter object compatible with KnowledgeRetriever LLM refinement
    """
    return LLMClientAdapter(llm_manager)
