import os
import asyncio
from ollama import Client, AsyncClient
from typing import List, Dict, Any, Optional, Union

class LLMClient:
    def __init__(self, host: str = "https://ollama.com", api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OLLAMA_API_KEY')
        self.headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
        self.client = Client(host=host, headers=self.headers)
        self.async_client = AsyncClient(host=host, headers=self.headers)

    def chat(self, model: str, messages: List[Dict[str, str]], stream: bool = False, temperature: float = 0.0) -> Union[str, Any]:
        """
        Synchronous chat completion using Ollama.
        """
        model = model.strip()
        options = {'temperature': temperature}
        if stream:
            return self.client.chat(model=model, messages=messages, stream=True, options=options)
        
        response = self.client.chat(model=model, messages=messages, stream=False, options=options)
        return response['message']['content']

    async def chat_async(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        """
        Asynchronous chat completion using Ollama.
        """
        model = model.strip()
        options = {'temperature': temperature}
        response = await self.async_client.chat(model=model, messages=messages, options=options)
        return response['message']['content']

# Centralized instance
_llm_instance = None

def get_llm_client() -> LLMClient:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance
