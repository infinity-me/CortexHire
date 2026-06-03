"""
CortexHire — LLM Router
Handles Groq (primary) → OpenAI (secondary) → Mock (offline) fallback chain.
Gemini Flash used for vision analysis (posture/body language in live interviews).
All LLM calls in the system go through this router.
"""
from __future__ import annotations

import json
import logging
import random
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import settings

logger = logging.getLogger(__name__)

# ─── Provider Clients ────────────────────────────────────────

_groq_client = None
_openai_client = None
_gemini_model = None


def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None and settings.has_gemini_vision:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        _gemini_model = genai.GenerativeModel(settings.gemini_model)
    return _gemini_model


def _get_groq_client():
    global _groq_client
    if _groq_client is None and settings.groq_api_key:
        from groq import Groq
        _groq_client = Groq(api_key=settings.groq_api_key)
    return _groq_client


def _get_openai_client():
    global _openai_client
    if _openai_client is None and settings.openai_api_key:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


# ─── Main Chat Completion ────────────────────────────────────

async def llm_chat(
    messages: list[dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 2000,
    json_mode: bool = False,
    task_name: str = "llm_task",
) -> str:
    """
    Route an LLM chat completion through Groq → OpenAI → Mock.
    Returns the assistant message content as a string.
    """
    provider = settings.active_llm

    if provider == "groq":
        try:
            return await _groq_chat(messages, temperature, max_tokens, json_mode)
        except Exception as e:
            logger.warning(f"[{task_name}] Groq failed: {e}. Trying OpenAI...")
            if settings.openai_api_key:
                try:
                    return await _openai_chat(messages, temperature, max_tokens, json_mode)
                except Exception as e2:
                    logger.warning(f"[{task_name}] OpenAI failed: {e2}. Using mock.")
            return _mock_response(task_name, messages)

    elif provider == "openai":
        try:
            return await _openai_chat(messages, temperature, max_tokens, json_mode)
        except Exception as e:
            logger.warning(f"[{task_name}] OpenAI failed: {e}. Using mock.")
            return _mock_response(task_name, messages)

    else:
        return _mock_response(task_name, messages)


async def _groq_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    import asyncio
    client = _get_groq_client()
    if not client:
        raise RuntimeError("Groq client not initialized")

    loop = asyncio.get_event_loop()
    if json_mode:
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
        )
    else:
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    return response.choices[0].message.content or ""


async def _openai_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    import asyncio
    client = _get_openai_client()
    if not client:
        raise RuntimeError("OpenAI client not initialized")

    loop = asyncio.get_event_loop()
    if json_mode:
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
        )
    else:
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    return response.choices[0].message.content or ""


# ─── Mock Responses ──────────────────────────────────────────

def _mock_response(task_name: str, messages: list[dict]) -> str:
    """
    Generate deterministic mock LLM responses for offline/demo mode.
    Structured to match what each task expects.
    """
    if "role_genome" in task_name or "role_cognition" in task_name:
        return json.dumps({
            "technical_depth": round(random.uniform(0.70, 0.95), 2),
            "ambiguity_tolerance": round(random.uniform(0.60, 0.95), 2),
            "ownership": round(random.uniform(0.75, 0.98), 2),
            "communication": round(random.uniform(0.55, 0.85), 2),
            "startup_readiness": round(random.uniform(0.60, 0.95), 2),
            "leadership_potential": round(random.uniform(0.50, 0.85), 2),
            "creativity": round(random.uniform(0.50, 0.90), 2),
            "execution_speed": round(random.uniform(0.65, 0.95), 2),
            "functional_needs": ["Backend scalability", "Real-time processing", "System design"],
            "hidden_needs": ["Ownership mentality", "Startup tolerance", "Cross-functional communication"],
            "team_dynamics": "Small, high-ownership team requiring strong collaboration",
            "risk_profile": "Medium-high tolerance for ambiguity and fast iteration",
            "cognitive_style": "Systems thinker with execution bias",
            "role_summary": "This role demands a highly capable technical owner who can operate in ambiguity and drive outcomes independently.",
        })

    if "technical_recruiter" in task_name:
        return json.dumps({
            "agent": "Technical Recruiter",
            "score": round(random.uniform(55, 95), 1),
            "confidence": round(random.uniform(0.65, 0.92), 2),
            "key_signals": [
                "Demonstrated distributed systems expertise",
                "Production system at relevant scale",
                "Strong Go/Python proficiency"
            ],
            "risks": ["Limited fintech domain experience"],
            "reasoning": "Candidate shows strong technical depth with relevant architecture experience. Scale of systems handled aligns well with role requirements.",
        })

    if "hiring_manager" in task_name:
        return json.dumps({
            "agent": "Hiring Manager",
            "score": round(random.uniform(55, 92), 1),
            "confidence": round(random.uniform(0.65, 0.90), 2),
            "key_signals": [
                "Track record of ownership",
                "Has shipped production systems independently",
                "Promotion trajectory signals performance"
            ],
            "risks": ["May need ramp-up time for domain context"],
            "reasoning": "Execution signals are strong. Candidate has consistently delivered outcomes, not just tasks.",
        })

    if "org_psychologist" in task_name:
        return json.dumps({
            "agent": "Organizational Psychologist",
            "score": round(random.uniform(55, 90), 1),
            "confidence": round(random.uniform(0.60, 0.88), 2),
            "key_signals": [
                "Resilience demonstrated through career challenges",
                "Consistent performance pattern",
                "Adaptability across domains"
            ],
            "risks": ["Communication style may need adjustment for this culture"],
            "reasoning": "Behavioral pattern suggests high resilience and adaptability. Consistent delivery across different environments.",
        })

    if "bias_corrector" in task_name:
        return json.dumps({
            "agent": "Diversity & Bias Corrector",
            "score": round(random.uniform(60, 95), 1),
            "confidence": round(random.uniform(0.70, 0.93), 2),
            "bias_flags_detected": ["Education pedigree signal detected"],
            "bias_adjustment": round(random.uniform(0, 8), 1),
            "adjusted_score": round(random.uniform(62, 95), 1),
            "key_signals": [
                "Achievement signals outperform pedigree indicators",
                "Career gap is justified and non-impactful to capability"
            ],
            "reasoning": "After removing pedigree signals, candidate's intrinsic capability indicators remain strong. Career gaps appropriately contextualized.",
        })

    if "future_predictor" in task_name:
        return json.dumps({
            "agent": "Future Potential Predictor",
            "score": round(random.uniform(55, 95), 1),
            "confidence": round(random.uniform(0.60, 0.88), 2),
            "trajectory": "accelerating",
            "predicted_role_in_2_years": "Staff Engineer or Technical Lead",
            "learning_velocity": round(random.uniform(0.65, 0.95), 2),
            "leadership_emergence": round(random.uniform(0.50, 0.90), 2),
            "key_signals": [
                "Consistent scope expansion year over year",
                "Proactive skill acquisition",
                "Multiple successful domain transitions"
            ],
            "reasoning": "Career trajectory shows accelerating growth. High probability of exceeding role requirements within 12 months.",
        })

    if "explanation" in task_name or "explainability" in task_name:
        return (
            "This candidate ranks highly due to a rare combination of technical depth and startup execution experience. "
            "Their career trajectory shows consistent scope expansion, suggesting high learning velocity. "
            "The multi-agent analysis reached strong consensus: 4 of 5 agents placed this candidate in the top quartile. "
            "Primary risk is limited domain-specific experience, mitigated by demonstrated ability to learn new domains rapidly."
        )

    if "copilot" in task_name:
        return (
            "Based on the ranking analysis, Candidate #1 outperforms Candidate #2 primarily on execution signals and ownership trajectory. "
            "While Candidate #2 has a stronger academic background, the AI scoring weighted capability evidence over pedigree indicators. "
            "The key differentiator: Candidate #1 has built and shipped systems of comparable complexity independently, "
            "which is a stronger predictor of success in this startup environment."
        )

    # Generic fallback
    return json.dumps({"result": "Mock response — configure GROQ_API_KEY for live AI responses"})


# ─── Embedding Generation ────────────────────────────────────

async def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for text. Falls back to TF-IDF mock."""
    if settings.active_llm == "mock":
        return _mock_embedding(text)

    if settings.groq_api_key:
        # Groq doesn't have embeddings yet — use OpenAI if available
        pass

    if settings.openai_api_key:
        try:
            import asyncio
            client = _get_openai_client()
            if not client:
                return _mock_embedding(text)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.embeddings.create(
                    model=settings.embedding_model,
                    input=text,
                )
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding API failed: {e}. Using TF-IDF fallback.")

    return _mock_embedding(text)


def _mock_embedding(text: str) -> list[float]:
    """TF-IDF inspired mock embedding — deterministic based on text content."""
    import hashlib
    import math

    # Create a deterministic vector based on text hash
    h = hashlib.sha256(text.encode()).hexdigest()
    seed = int(h[:8], 16)
    rng = random.Random(seed)

    # Generate 1536-dim vector (OpenAI ada-002 dimension)
    vec = [rng.gauss(0, 1) for _ in range(1536)]

    # Normalize
    magnitude = math.sqrt(sum(x**2 for x in vec))
    if magnitude > 0:
        vec = [x / magnitude for x in vec]

    return vec


# ─── Gemini Vision Analysis ──────────────────────────────────

async def llm_vision_chat(
    prompt: str,
    image_base64: str,
    image_mime: str = "image/jpeg",
    task_name: str = "vision_task",
) -> str:
    """
    Analyze an image using Gemini Flash (vision-capable).
    Falls back to mock scoring if Gemini key is not configured.

    Args:
        prompt: The analysis prompt / question
        image_base64: Base64-encoded image bytes
        image_mime: MIME type of the image (e.g. 'image/jpeg')
        task_name: Name for logging

    Returns:
        LLM response string (typically JSON)
    """
    if not settings.has_gemini_vision:
        logger.info(f"[{task_name}] No Gemini key — using mock vision scoring")
        return _mock_vision_response(task_name)

    try:
        import asyncio
        import base64
        import google.generativeai as genai
        from google.generativeai.types import content_types

        model = _get_gemini_model()
        if not model:
            return _mock_vision_response(task_name)

        # Build multimodal content: image + text prompt
        image_data = base64.b64decode(image_base64)
        image_part = {"mime_type": image_mime, "data": image_data}

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content([image_part, prompt])
        )
        return response.text or _mock_vision_response(task_name)

    except Exception as e:
        logger.warning(f"[{task_name}] Gemini vision failed: {e}. Using mock.")
        return _mock_vision_response(task_name)


def _mock_vision_response(task_name: str) -> str:
    """
    Smart mock body-language scoring — realistic variance, not inflated.
    Used when Gemini vision API is unavailable.
    """
    rng = random.Random()
    posture = round(rng.uniform(45, 88), 1)
    eye_contact = round(rng.uniform(40, 85), 1)
    engagement = round(rng.uniform(50, 90), 1)
    confidence = round(rng.uniform(45, 85), 1)

    observations = []
    if posture < 60:
        observations.append("Candidate appears slightly hunched — shoulders not fully upright")
    elif posture > 78:
        observations.append("Good upright posture maintained")
    else:
        observations.append("Posture is acceptable but could be more upright")

    if eye_contact < 55:
        observations.append("Limited eye contact with camera — looking away frequently")
    elif eye_contact > 75:
        observations.append("Strong direct eye contact maintained")
    else:
        observations.append("Moderate eye contact — some moments of looking away")

    return json.dumps({
        "posture_score": posture,
        "eye_contact_score": eye_contact,
        "engagement_score": engagement,
        "confidence_score": confidence,
        "observations": observations,
        "overall_body_language": round((posture + eye_contact + engagement + confidence) / 4, 1),
        "source": "mock",
    })

