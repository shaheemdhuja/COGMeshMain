"""Ollama Provider implementing async HTTP communication with local Ollama LLM endpoint."""

from typing import Any, Dict, Optional
import httpx
from loguru import logger

from app.core.config import settings


class OllamaProvider:
    """Wrapper provider communicating with local Ollama service for LLM text generation and JSON tasks."""

    def __init__(self, host: Optional[str] = None, default_model: Optional[str] = None):
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.default_model = default_model or settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        json_format: bool = False,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """Send completion prompt to Ollama HTTP API endpoint and return response payload."""
        target_model = model or self.default_model
        endpoint = f"{self.host}/api/generate"

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_format:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(endpoint, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "response": data.get("response", ""),
                        "provider": "OllamaProvider",
                        "model": target_model,
                        "done": data.get("done", True),
                    }
                else:
                    logger.warning(
                        f"[OllamaProvider] Endpoint returned HTTP {response.status_code}: {response.text}"
                    )
                    return {
                        "error": f"Ollama HTTP {response.status_code}",
                        "provider": "OllamaProvider",
                        "model": target_model,
                    }
        except Exception as exc:
            logger.warning(f"[OllamaProvider] Service unavailable at {self.host}: {str(exc)}")
            return {
                "error": f"Ollama service unavailable: {str(exc)}",
                "provider": "OllamaProvider",
                "model": target_model,
            }
