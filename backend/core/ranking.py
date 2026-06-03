"""
CortexHire — Consensus Ranking Engine

Aggregates all 5 agent scores + embedding similarity + temporal momentum + bias correction
into a final consensus ranking with explainable scores.

Final Output per candidate:
  - fit_score          : Overall capability-to-role match (0–100)
  - risk_score         : Delivery and performance risk (0–100, lower = less risk)
  - growth_score       : Future potential and trajectory (0–100)
  - confidence_score   : System confidence in this ranking (0–100)
  - success_probability: Predicted probability of success in role (0–1)
  - rank_position      : Final rank in shortlist
  - explanation        : Human-readable reasoning
  - agent_scores       : All 5 agent results
  - bias_report        : Bias analysis results
"""
from __future__ import annotations

import logging
from typing import Any

from core.llm_router import llm_chat
from core.bias_correction import (
    detect_bias_signals,
    apply_bias_correction,
    compute_fairness_score,
)

logger = logging.getLogger(__name__)

# Agent weight configuration
AGENT_WEIGHTS = {
    "Technical Recruiter": 0.28,
    "Hiring Manager": 0.25,
    "Organizational Psychologist": 0.18,
    "Diversity & Bias Corrector": 0.15,
    "Future Potential Predictor": 0.14,
}


def compute_consensus_score(
    agent_results: list[dict],
    embedding_similarity: float,
    temporal_profile: dict,
    bias_analysis: dict,
    role_genome: dict,
) -> dict[str, Any]:
    """
    Aggregate all signals into a consensus ranking score.
    """
    # ── Agent Score Aggregation ──────────────────────────────
    agent_scores_map = {}
    weighted_agent_score = 0.0
    total_weight = 0.0
    total_confidence = 0.0

    for agent in agent_results:
        name = agent.get("agent", "Unknown")
        score = float(agent.get("score", 60.0))
        confidence = float(agent.get("confidence", 0.5))
        weight = AGENT_WEIGHTS.get(name, 0.15)

        # Confidence-weighted contribution
        effective_weight = weight * confidence
        weighted_agent_score += score * effective_weight
        total_weight += effective_weight
        total_confidence += confidence
        agent_scores_map[name] = {
            "score": round(score, 1),
            "confidence": round(confidence, 2),
            "weight": weight,
        }

    raw_agent_score = weighted_agent_score / total_weight if total_weight > 0 else 60.0
    avg_confidence = total_confidence / len(agent_results) if agent_results else 0.5

    # ── Embedding Similarity ─────────────────────────────────
    # Convert cosine similarity (0–1) to 0–100 score
    embedding_score = embedding_similarity * 100

    # ── Temporal Momentum ────────────────────────────────────
    momentum_score = temporal_profile.get("momentum_score", 0.5) * 100
    trajectory = temporal_profile.get("trajectory", "steady")

    # Trajectory bonus/penalty
    trajectory_modifier = {
        "accelerating": 5.0,
        "steady": 0.0,
        "plateauing": -5.0,
        "declining": -10.0,
        "unknown": 0.0,
    }.get(trajectory, 0.0)

    # ── Bias Correction ──────────────────────────────────────
    bias_flags = bias_analysis.get("bias_flags", [])
    bias_adjustment = bias_analysis.get("raw_adjustment", 0.0)

    # ── Composite Fit Score ──────────────────────────────────
    # Weights: agent scores (50%) + embedding similarity (30%) + temporal momentum (20%)
    composite = (
        raw_agent_score * 0.50 +
        embedding_score * 0.30 +
        momentum_score * 0.20
    )

    # Apply trajectory modifier
    composite += trajectory_modifier

    # Apply bias correction
    fit_score = apply_bias_correction(composite, bias_analysis)
    fit_score = round(max(0.0, min(100.0, fit_score)), 1)

    # ── Risk Score ───────────────────────────────────────────
    # Invert hiring manager + future predictor "risk" signals
    hiring_manager = next((a for a in agent_results if a.get("agent") == "Hiring Manager"), {})
    future_predictor = next((a for a in agent_results if a.get("agent") == "Future Potential Predictor"), {})

    hm_score = float(hiring_manager.get("score", 60.0))
    fp_score = float(future_predictor.get("score", 60.0))
    risk_raw = 100.0 - ((hm_score * 0.6 + fp_score * 0.4))  # Higher = more risk

    # Reduce risk for accelerating trajectories
    if trajectory == "accelerating":
        risk_raw -= 8
    elif trajectory == "declining":
        risk_raw += 10

    risk_score = round(max(0.0, min(100.0, risk_raw)), 1)

    # ── Growth Score ─────────────────────────────────────────
    fp_score_val = float(future_predictor.get("score", 60.0))
    learning_velocity = float(future_predictor.get("learning_velocity", 0.65)) * 100
    leadership_emergence = float(future_predictor.get("leadership_emergence", 0.55)) * 100

    growth_score = round(
        fp_score_val * 0.50 +
        learning_velocity * 0.25 +
        leadership_emergence * 0.25,
        1
    )

    # ── Confidence Score ─────────────────────────────────────
    # How confident is the system in this ranking?
    agent_agreement = _compute_agent_agreement(agent_results)
    confidence_score = round(
        avg_confidence * 60 +
        agent_agreement * 40,
        1
    )

    # ── Success Probability ──────────────────────────────────
    # Sigmoid-like function anchored at fit=70 → 50% probability
    success_prob = _score_to_probability(fit_score)

    return {
        "fit_score": fit_score,
        "risk_score": risk_score,
        "growth_score": round(growth_score, 1),
        "confidence_score": round(confidence_score, 1),
        "success_probability": round(success_prob, 3),
        "raw_agent_score": round(raw_agent_score, 1),
        "embedding_similarity": round(embedding_similarity, 4),
        "trajectory": trajectory,
        "bias_adjustment": round(bias_adjustment, 1),
        "agent_scores": agent_scores_map,
    }


def _compute_agent_agreement(agent_results: list[dict]) -> float:
    """
    Measure agreement between agents (0–1).
    High agreement = high confidence. Wide spread = low confidence.
    """
    scores = [float(a.get("score", 60.0)) for a in agent_results]
    if len(scores) < 2:
        return 0.6

    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5

    # std_dev of 0 = perfect agreement (1.0), std_dev of 20+ = high disagreement (0.0)
    agreement = max(0.0, 1.0 - (std_dev / 20.0))
    return round(agreement, 3)


def _score_to_probability(fit_score: float) -> float:
    """Convert fit score to success probability using sigmoid-like curve."""
    import math
    # Anchored: score 70 → ~55% probability, score 90 → ~85%
    x = (fit_score - 65) / 12
    return round(1 / (1 + math.exp(-x)), 3)


async def generate_explanation(
    candidate: dict,
    job: dict,
    consensus: dict,
    agent_results: list[dict],
    bias_analysis: dict,
) -> str:
    """
    Generate a human-readable explanation of why this candidate is ranked here.
    Innovation #5 — Explainability Layer.
    """
    # Build summary of agent consensus
    top_signals = []
    all_risks = []
    for agent in agent_results:
        signals = agent.get("key_signals", [])
        risks = agent.get("risks", [])
        top_signals.extend(signals[:2])
        all_risks.extend(risks[:1])

    bias_flags = bias_analysis.get("bias_flags", [])

    context = f"""
Candidate: {candidate.get('name', '')}
Role: {job.get('title', '')} at {job.get('company', '')}

Scoring Summary:
  Fit Score: {consensus['fit_score']}/100
  Risk Score: {consensus['risk_score']}/100 (lower is better)
  Growth Score: {consensus['growth_score']}/100
  Success Probability: {consensus['success_probability']*100:.0f}%
  Career Trajectory: {consensus['trajectory']}

Top Signals From All Agents:
{chr(10).join(f'  - {s}' for s in top_signals[:6])}

Key Risks Identified:
{chr(10).join(f'  - {r}' for r in all_risks[:3])}

Bias Flags: {', '.join(bias_flags) if bias_flags else 'None'}
Bias Score Adjustment: {consensus['bias_adjustment']:+.1f} points

Write a clear, concise 3-paragraph explanation of:
1. Why this candidate scores as they do — specific evidence
2. Key strengths and how they match the role
3. Risks and whether/why they are acceptable
Be direct, honest, and recruiter-friendly. No corporate speak.
"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert talent analyst writing candidate assessment summaries for recruiters. Be concise, evidence-based, and honest about both strengths and concerns.",
        },
        {"role": "user", "content": context},
    ]

    try:
        explanation = await llm_chat(
            messages=messages,
            temperature=0.4,
            max_tokens=600,
            json_mode=False,
            task_name="explainability_explanation",
        )
        return explanation
    except Exception as e:
        logger.warning(f"Explanation generation failed: {e}")
        return f"Candidate scored {consensus['fit_score']}/100 fit score with {consensus['trajectory']} career trajectory. {', '.join(top_signals[:3])}."


def rank_candidates(
    scored_candidates: list[dict],
    shortlist_size: int = 10,
) -> list[dict]:
    """
    Sort candidates by fit_score and assign rank positions.
    Returns top shortlist_size candidates.
    """
    sorted_candidates = sorted(
        scored_candidates,
        key=lambda c: (
            c["consensus"]["fit_score"],
            c["consensus"]["growth_score"],
            -c["consensus"]["risk_score"],
        ),
        reverse=True,
    )

    ranked = []
    for i, candidate_data in enumerate(sorted_candidates[:shortlist_size]):
        candidate_data["rank_position"] = i + 1
        candidate_data["shortlisted"] = True
        ranked.append(candidate_data)

    return ranked
