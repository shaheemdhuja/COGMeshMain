"""Real AI Execution Demonstration Script for CogMesh.

Pipeline:
Image/PDF -> Tesseract OCR -> Gemma Summary (Ollama) -> Translation -> MCQ Generation.
Saves intermediate outputs in demo/ directory and measures execution latency.
"""

import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Any, Dict
from PIL import Image, ImageDraw, ImageFont


from app.tasks.adapters.mcq_adapter import MCQAdapter
from app.tasks.adapters.ocr_adapter import OCRAdapter
from app.tasks.adapters.summarization_adapter import SummaryAdapter
from app.tasks.adapters.translation_adapter import TranslationAdapter
from app.tasks.enums import TaskStatus
from app.tasks.providers.ollama_provider import OllamaProvider
from app.tasks.providers.tesseract_provider import TesseractProvider


class MissingProviderError(Exception):
    """Exception raised when an external AI provider engine is missing or unavailable."""
    pass


def create_sample_lecture_image(output_path: str) -> str:
    """Create a sample lecture image containing clear text for OCR testing."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (800, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text = (
        "CogMesh is a collaborative multi-device edge AI runtime for distributed intelligence.\n"
        "It optimizes execution graphs across heterogeneous edge nodes based on hardware constraints."
    )
    draw.text((20, 40), text, fill=(0, 0, 0))
    img.save(output_path)
    return output_path


async def verify_real_providers() -> None:
    """Verify that Tesseract OCR binary and Ollama service are active."""
    # Check 1: Tesseract OCR
    tess_provider = TesseractProvider()
    ocr_test = await tess_provider.extract_text({"image_path": "demo/lecture_sample.png"})
    if "error" in ocr_test and "not installed" in ocr_test["error"].lower():
        raise MissingProviderError(
            "Tesseract OCR binary (tesseract.exe) is not installed on system PATH.\n"
            "Required dependency: Install Tesseract-OCR from https://github.com/UB-Mannheim/tesseract/wiki"
        )

    # Check 2: Ollama Service
    ollama_provider = OllamaProvider()
    ollama_test = await ollama_provider.generate(prompt="ping", timeout=2.0)
    if "error" in ollama_test and "unavailable" in ollama_test["error"].lower():
        raise MissingProviderError(
            "Local Ollama service is not running on http://localhost:11434.\n"
            "Required dependency: Install Ollama from https://ollama.com and run 'ollama pull gemma3:latest'"
        )


async def run_demonstration():
    """Execute full 4-step AI pipeline with real providers and measure latency."""
    demo_dir = "demo"
    os.makedirs(demo_dir, exist_ok=True)
    sample_image = create_sample_lecture_image(os.path.join(demo_dir, "lecture_sample.png"))

    print("\n=======================================================")
    print(" CogMesh Real AI Provider Execution Demonstration")
    print("=======================================================\n")

    # Step 0: Check Provider Availability
    try:
        print("[1/5] Verifying external AI provider engines...")
        await verify_real_providers()
        print("  -> Tesseract OCR binary: ONLINE")
        print("  -> Ollama LLM Service: ONLINE")
    except MissingProviderError as exc:
        print("\n[STOPPED] Provider Dependency Missing:")
        print(f"  {exc}")
        print("\nPipeline execution stopped immediately to prevent mock fallback.")
        return False

    start_total = time.perf_counter()

    # Step 1: OCR
    print("\n[2/5] Running Tesseract OCR on lecture image...")
    t_ocr_start = time.perf_counter()
    ocr_adapter = OCRAdapter()
    ocr_result = await ocr_adapter.execute({"image_path": sample_image})
    ocr_time = round((time.perf_counter() - t_ocr_start) * 1000, 2)
    ocr_text = ocr_result.output.get("text", "")
    with open(os.path.join(demo_dir, "ocr.txt"), "w", encoding="utf-8") as f:
        f.write(ocr_text)
    print(f"  -> Saved demo/ocr.txt (Latency: {ocr_time}ms)")

    # Step 2: Summarization
    print("\n[3/5] Running Gemma Text Summarization via Ollama...")
    t_sum_start = time.perf_counter()
    sum_adapter = SummaryAdapter()
    sum_result = await sum_adapter.execute({"text": ocr_text})
    sum_time = round((time.perf_counter() - t_sum_start) * 1000, 2)
    summary_text = sum_result.output.get("summary", "")
    with open(os.path.join(demo_dir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"  -> Saved demo/summary.txt (Latency: {sum_time}ms)")

    # Step 3: Translation
    print("\n[4/5] Running Neural Text Translation...")
    t_trans_start = time.perf_counter()
    trans_adapter = TranslationAdapter()
    trans_result = await trans_adapter.execute({"text": summary_text, "target_lang": "Spanish"})
    trans_time = round((time.perf_counter() - t_trans_start) * 1000, 2)
    translation_text = trans_result.output.get("translated_text", "")
    with open(os.path.join(demo_dir, "translation.txt"), "w", encoding="utf-8") as f:
        f.write(translation_text)
    print(f"  -> Saved demo/translation.txt (Latency: {trans_time}ms)")

    # Step 4: MCQ Generation
    print("\n[5/5] Running MCQ Question Generation via Ollama...")
    t_mcq_start = time.perf_counter()
    mcq_adapter = MCQAdapter()
    mcq_result = await mcq_adapter.execute({"text": summary_text})
    mcq_time = round((time.perf_counter() - t_mcq_start) * 1000, 2)
    mcqs_data = mcq_result.output.get("questions", [])
    with open(os.path.join(demo_dir, "mcqs.json"), "w", encoding="utf-8") as f:
        json.dump(mcqs_data, f, indent=2)
    print(f"  -> Saved demo/mcqs.json (Latency: {mcq_time}ms)")

    total_time = round((time.perf_counter() - start_total) * 1000, 2)

    # Step 5: Metrics Summary
    metrics = {
        "ocr_time_ms": ocr_time,
        "summarization_time_ms": sum_time,
        "translation_time_ms": trans_time,
        "mcq_generation_time_ms": mcq_time,
        "total_execution_time_ms": total_time,
        "providers_used": {
            "ocr": "TesseractProvider (tesseract-ocr)",
            "summarization": "OllamaProvider (gemma3:latest)",
            "translation": "TranslationProvider (nllb-200)",
            "mcq_generation": "OllamaProvider (gemma3:latest)",
        },
    }
    with open(os.path.join(demo_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n-> Saved demo/metrics.json (Total Pipeline Latency: {total_time}ms)")
    print("\n=======================================================")
    print(" Real AI Provider Demonstration Completed Successfully!")
    print("=======================================================\n")
    return True


if __name__ == "__main__":
    asyncio.run(run_demonstration())
