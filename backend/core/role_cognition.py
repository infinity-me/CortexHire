"""
CortexHire — Innovation #1: Role Cognition Engine

Transforms noisy, inflated job descriptions into structured "Role Genomes" —
a scored multidimensional model of what a role ACTUALLY needs, beyond keywords.

Role Genome dimensions:
  - technical_depth     : Complexity and sophistication of technical work
  - ambiguity_tolerance : Comfort with unclear requirements and fast change
  - ownership           : Expectation for initiative and independent delivery
  - communication       : Cross-functional and stakeholder interaction needs
  - startup_readiness   : Comfort with startup uncertainty, speed, and chaos
  - leadership_potential: Expected influence over people or technical direction
  - creativity          : Novel problem-solving vs. well-defined execution
  - execution_speed     : Bias toward fast shipping vs. careful deliberation

Plus extracted structured intelligence about:
  - functional_needs    : What the role actually does
  - hidden_needs        : What the JD doesn't say but implies
  - team_dynamics       : Team structure and culture signals
  - risk_profile        : Risk tolerance in the role
  - cognitive_style     : Thinking style required
"""
from __future__ import annotations

import json
import logging
from typing import Any

from core.llm_router import llm_chat

logger = logging.getLogger(__name__)

ROLE_GENOME_SYSTEM_PROMPT = """
You are an elite talent intelligence system trained on thousands of hiring outcomes.

Your task: Analyze a job description and produce a structured "Role Genome" — 
a deep understanding of what the role ACTUALLY needs, beyond the surface-level keywords.

Job descriptions are often noisy, inflated, and inaccurate. Your job is to see through 
the noise and extract the true organizational intent.

You must return a valid JSON object with EXACTLY these fields:

{
  "technical_depth": <0.0-1.0>,
  "ambiguity_tolerance": <0.0-1.0>,
  "ownership": <0.0-1.0>,
  "communication": <0.0-1.0>,
  "startup_readiness": <0.0-1.0>,
  "leadership_potential": <0.0-1.0>,
  "creativity": <0.0-1.0>,
  "execution_speed": <0.0-1.0>,
  "functional_needs": [<list of 3-5 actual functional requirements>],
  "hidden_needs": [<list of 3-5 non-obvious implicit requirements>],
  "team_dynamics": "<one sentence about team structure and culture>",
  "risk_profile": "<one sentence about risk and ambiguity tolerance>",
  "cognitive_style": "<one sentence about required thinking style>",
  "role_summary": "<2-3 sentences synthesizing the true essence of this role>"
}

Scoring guidelines:
- technical_depth 0.9+: requires deep systems expertise, not just familiarity
- ambiguity_tolerance 0.8+: startup/0→1 environment, no playbook
- ownership 0.9+: fully independent ownership, high stakes
- startup_readiness 0.8+: explicitly values startup experience or speed > process
- leadership_potential 0.7+: managing others or significant technical influence expected
- creativity 0.8+: novel problem-solving, not well-defined execution
- execution_speed 0.9+: extreme bias toward speed, "move fast" culture

Do not be literal. Think about what success in this role actually requires.
"""


async def extract_role_genome(job_description: str, job_title: str = "", company: str = "") -> dict[str, Any]:
    """
    Extract the Role Genome from a job description.
    Returns a structured dict with scores and intelligence.
    """
    context = f"Company: {company}\nTitle: {job_title}\n\n{job_description}" if company else job_description

    messages = [
        {"role": "system", "content": ROLE_GENOME_SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this job description:\n\n{context}"},
    ]

    try:
        raw = await llm_chat(
            messages=messages,
            temperature=0.2,
            max_tokens=1500,
            json_mode=True,
            task_name="role_cognition_role_genome",
        )
        genome = json.loads(raw)
        genome = _validate_and_normalize_genome(genome)
        logger.info(f"Role Genome extracted for '{job_title}' with {len(genome)} dimensions")
        return genome
    except Exception as e:
        logger.error(f"Role Genome extraction failed: {e}")
        return _default_genome()


def _validate_and_normalize_genome(genome: dict) -> dict:
    """Ensure all required fields exist and scores are within [0,1]."""
    scalar_fields = [
        "technical_depth", "ambiguity_tolerance", "ownership",
        "communication", "startup_readiness", "leadership_potential",
        "creativity", "execution_speed",
    ]
    list_fields = ["functional_needs", "hidden_needs"]
    str_fields = ["team_dynamics", "risk_profile", "cognitive_style", "role_summary"]

    defaults = _default_genome()

    for field in scalar_fields:
        val = genome.get(field, defaults[field])
        genome[field] = max(0.0, min(1.0, float(val if val is not None else defaults[field])))

    for field in list_fields:
        if field not in genome or not isinstance(genome[field], list):
            genome[field] = defaults[field]

    for field in str_fields:
        if field not in genome or not isinstance(genome[field], str):
            genome[field] = defaults[field]

    return genome


def _default_genome() -> dict:
    """Fallback genome when extraction fails."""
    return {
        "technical_depth": 0.75,
        "ambiguity_tolerance": 0.70,
        "ownership": 0.80,
        "communication": 0.65,
        "startup_readiness": 0.70,
        "leadership_potential": 0.55,
        "creativity": 0.65,
        "execution_speed": 0.75,
        "functional_needs": ["Technical problem solving", "System design", "Code quality"],
        "hidden_needs": ["Ownership mentality", "Collaboration", "Fast learning"],
        "team_dynamics": "Small collaborative team requiring strong communication",
        "risk_profile": "Moderate risk tolerance with bias toward action",
        "cognitive_style": "Pragmatic systems thinker",
        "role_summary": "This role requires strong technical capability combined with ownership mindset.",
    }


def genome_to_text_description(genome: dict) -> str:
    """Convert a Role Genome to a rich text description for embedding generation."""
    lines = [
        f"Role requires technical depth at {genome['technical_depth']:.0%} level.",
        f"Ambiguity tolerance required: {genome['ambiguity_tolerance']:.0%}.",
        f"Ownership expectation: {genome['ownership']:.0%}.",
        f"Communication demands: {genome['communication']:.0%}.",
        f"Startup readiness needed: {genome['startup_readiness']:.0%}.",
        f"Leadership potential expected: {genome['leadership_potential']:.0%}.",
        f"Creativity required: {genome['creativity']:.0%}.",
        f"Execution speed expectation: {genome['execution_speed']:.0%}.",
        "",
        f"Functional needs: {', '.join(genome.get('functional_needs', []))}.",
        f"Hidden needs: {', '.join(genome.get('hidden_needs', []))}.",
        f"Team dynamics: {genome.get('team_dynamics', '')}",
        f"Risk profile: {genome.get('risk_profile', '')}",
        f"Cognitive style: {genome.get('cognitive_style', '')}",
        f"Role essence: {genome.get('role_summary', '')}",
    ]
    return " ".join(lines)
