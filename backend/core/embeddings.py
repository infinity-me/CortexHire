"""
CortexHire — Innovation #3: Human Capability Embeddings

Generates multi-dimensional capability vectors for candidates.
Each dimension is embedded separately for targeted semantic search.

Capability Dimensions:
  - technical_depth   : Complexity and sophistication of technical work
  - adaptability      : Speed of learning, domain switching, ambiguity tolerance
  - leadership        : Team influence, mentorship, direction-setting
  - execution         : Delivery track record, shipping ability
  - systems_thinking  : Architectural reasoning, big-picture design
  - creativity        : Novel problem-solving, innovation history
  - resilience        : Performance under pressure, recovery from setbacks
  - communication     : Cross-functional articulation, stakeholder management
"""
from __future__ import annotations

import logging
import math
from typing import Any

from core.llm_router import get_embedding

logger = logging.getLogger(__name__)

CAPABILITY_DIMENSIONS = [
    "technical_depth",
    "adaptability",
    "leadership",
    "execution",
    "systems_thinking",
    "creativity",
    "resilience",
    "communication",
]


def _build_dimension_text(candidate: dict, dimension: str) -> str:
    """
    Build a focused text representation of a candidate for a specific capability dimension.
    """
    name = candidate.get("name", "")
    summary = candidate.get("summary", "")
    achievements = candidate.get("achievements", [])
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])
    cap_profile = candidate.get("capability_profile", {})

    skill_names = [s["name"] if isinstance(s, dict) else s for s in skills]
    achievement_text = ". ".join(achievements[:3]) if achievements else ""
    career_summary = " ".join([
        "{} at {} ({})".format(r.get("title", ""), r.get("company", ""), r.get("description", ""))
        for r in career[:3]
    ])

    score = cap_profile.get(dimension, 0.7)

    # Build team sizes string without backslash in f-string
    team_sizes = ", ".join([str(r.get("team_size", 0)) for r in career])
    impact_scores = ", ".join(["{:.2f}".format(r.get("impact_score", 0)) for r in career])

    dimension_contexts = {
        "technical_depth": (
            "Technical expertise and complexity profile. Score: {:.2f}. "
            "Skills: {}. "
            "Technical achievements: {}. "
            "Technical career: {}"
        ).format(score, ", ".join(skill_names[:8]), achievement_text, career_summary),

        "adaptability": (
            "Adaptability, learning velocity, and domain transitions. Score: {:.2f}. "
            "Career transitions and growth: {}. "
            "Background: {}"
        ).format(score, career_summary, summary[:400]),

        "leadership": (
            "Leadership, team management, and organizational influence. Score: {:.2f}. "
            "Team sizes led: {}. "
            "Leadership evidence: {}. "
            "Career context: {}"
        ).format(score, team_sizes, achievement_text, career_summary),

        "execution": (
            "Execution ability, delivery track record, and output quality. Score: {:.2f}. "
            "Delivery achievements: {}. "
            "Impact scores by role: {}. "
            "Career: {}"
        ).format(score, achievement_text, impact_scores, career_summary),

        "systems_thinking": (
            "Systems architecture, design thinking, and technical breadth. Score: {:.2f}. "
            "Systems built: {}. "
            "Technical scope: {}"
        ).format(score, achievement_text, career_summary),

        "creativity": (
            "Creative problem-solving, innovation, and novel approaches. Score: {:.2f}. "
            "Innovations: {}. "
            "Context: {}"
        ).format(score, achievement_text, summary[:300]),

        "resilience": (
            "Resilience, persistence, and performance under pressure. Score: {:.2f}. "
            "Challenges overcome: {}. "
            "Career stability and growth: {}"
        ).format(score, summary[:400], career_summary),

        "communication": (
            "Communication, stakeholder management, and cross-functional work. Score: {:.2f}. "
            "Communication context: {}. "
            "Context: {}"
        ).format(score, career_summary, summary[:300]),
    }

    return dimension_contexts.get(dimension, "{}: {}".format(dimension, summary[:400]))


async def generate_candidate_embeddings(candidate: dict) -> dict[str, list[float]]:
    """
    Generate capability embeddings for all dimensions.
    Returns a dict of dimension_name → embedding_vector.
    """
    embeddings = {}
    for dimension in CAPABILITY_DIMENSIONS:
        text = _build_dimension_text(candidate, dimension)
        try:
            vec = await get_embedding(text)
            embeddings[dimension] = vec
        except Exception as e:
            logger.warning("Embedding failed for {}: {}. Using zero vector.".format(dimension, e))
            embeddings[dimension] = [0.0] * 1536

    logger.info("Generated {} capability embeddings for {}".format(len(embeddings), candidate.get("name", "unknown")))
    return embeddings


async def generate_role_embeddings(role_genome: dict, role_description: str) -> dict[str, list[float]]:
    """
    Generate role requirement embeddings from Role Genome dimensions.
    """
    embeddings = {}

    hidden_needs = ", ".join(role_genome.get("hidden_needs", []))
    functional_needs = ", ".join(role_genome.get("functional_needs", []))
    cognitive_style = role_genome.get("cognitive_style", "")
    team_dynamics = role_genome.get("team_dynamics", "")
    risk_profile = role_genome.get("risk_profile", "")

    dimension_map = {
        "technical_depth": "Role requires technical depth {:.0%}. {}".format(
            role_genome.get("technical_depth", 0.7), role_description[:500]
        ),
        "adaptability": "Role requires adaptability/ambiguity tolerance {:.0%}. Hidden needs: {}".format(
            role_genome.get("ambiguity_tolerance", 0.7), hidden_needs
        ),
        "leadership": "Role requires leadership {:.0%}. {}".format(
            role_genome.get("leadership_potential", 0.5), functional_needs
        ),
        "execution": "Role requires execution speed {:.0%} and ownership {:.0%}.".format(
            role_genome.get("execution_speed", 0.7), role_genome.get("ownership", 0.8)
        ),
        "systems_thinking": "Cognitive style: {}. Technical depth: {:.0%}.".format(
            cognitive_style, role_genome.get("technical_depth", 0.7)
        ),
        "creativity": "Role requires creativity {:.0%}. Hidden needs: {}".format(
            role_genome.get("creativity", 0.6), hidden_needs
        ),
        "resilience": "Role risk profile: {}. Startup readiness required: {:.0%}.".format(
            risk_profile, role_genome.get("startup_readiness", 0.7)
        ),
        "communication": "Role requires communication {:.0%}. Team dynamics: {}".format(
            role_genome.get("communication", 0.6), team_dynamics
        ),
    }

    for dimension, text in dimension_map.items():
        try:
            vec = await get_embedding(text)
            embeddings[dimension] = vec
        except Exception as e:
            logger.warning("Role embedding failed for {}: {}".format(dimension, e))
            embeddings[dimension] = [0.0] * 1536

    return embeddings


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a**2 for a in vec_a))
    mag_b = math.sqrt(sum(b**2 for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def compute_dimension_similarity(
    candidate_embeddings: dict[str, list[float]],
    role_embeddings: dict[str, list[float]],
    role_genome: dict,
) -> dict[str, float]:
    """
    Compute weighted semantic similarity per capability dimension.
    """
    similarities = {}
    for dimension in CAPABILITY_DIMENSIONS:
        c_vec = candidate_embeddings.get(dimension, [])
        r_vec = role_embeddings.get(dimension, [])
        similarities[dimension] = cosine_similarity(c_vec, r_vec)

    return similarities


def aggregate_similarity_score(
    similarities: dict[str, float],
    role_genome: dict,
) -> float:
    """
    Compute a weighted aggregate similarity score (0–1) based on role importance.
    """
    weights = {
        "technical_depth": role_genome.get("technical_depth", 0.75),
        "adaptability": role_genome.get("ambiguity_tolerance", 0.70),
        "leadership": role_genome.get("leadership_potential", 0.55),
        "execution": (role_genome.get("execution_speed", 0.75) + role_genome.get("ownership", 0.80)) / 2,
        "systems_thinking": role_genome.get("technical_depth", 0.75) * 0.8,
        "creativity": role_genome.get("creativity", 0.65),
        "resilience": role_genome.get("startup_readiness", 0.70),
        "communication": role_genome.get("communication", 0.65),
    }

    total_weight = sum(weights.values())
    weighted_sum = sum(
        similarities.get(dim, 0) * weight
        for dim, weight in weights.items()
    )

    return weighted_sum / total_weight if total_weight > 0 else 0.0
