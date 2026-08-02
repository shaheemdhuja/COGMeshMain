"""Integration and unit tests for Real AI Providers (TesseractProvider, OllamaProvider, TranslationProvider)."""

import pytest
from PIL import Image

from app.tasks.providers.ollama_provider import OllamaProvider
from app.tasks.providers.tesseract_provider import TesseractProvider
from app.tasks.providers.translation_provider import TranslationProvider


@pytest.mark.asyncio
async def test_tesseract_provider_with_pil_image() -> None:
    """Test TesseractProvider with a dynamically generated Pillow test image."""
    provider = TesseractProvider()
    img = Image.new("RGB", (100, 30), color=(255, 255, 255))
    res = await provider.extract_text(img)
    assert isinstance(res, dict)
    assert "provider" in res
    assert res["provider"] == "TesseractProvider"


@pytest.mark.asyncio
async def test_tesseract_provider_fallback_handling() -> None:
    """Test TesseractProvider graceful error handling on invalid image path."""
    provider = TesseractProvider(tesseract_cmd="invalid_path_to_tesseract")
    res = await provider.extract_text({"invalid": "payload"})
    assert isinstance(res, dict)
    assert "text" in res or "error" in res


@pytest.mark.asyncio
async def test_ollama_provider_unreachable_endpoint() -> None:
    """Test OllamaProvider graceful error handling when service is unreachable."""
    provider = OllamaProvider(host="http://127.0.0.1:59999")  # Unreachable port
    res = await provider.generate(prompt="Hello", timeout=0.1)
    assert isinstance(res, dict)
    assert "error" in res
    assert res["provider"] == "OllamaProvider"


@pytest.mark.asyncio
async def test_translation_provider_execution() -> None:
    """Test TranslationProvider execution and fallback."""
    provider = TranslationProvider()
    res = await provider.translate("Hello world", source_lang="English", target_lang="Spanish")
    assert isinstance(res, dict)
    assert "translated_text" in res
    assert res["target_language"] == "Spanish"
