"""
CortexHire — Innovation #8: Ethical AI / Bias Correction Layer

Detects and corrects systemic hiring biases in candidate evaluation:
  1. College prestige bias      — IIT/FAANG halo unrelated to capability
  2. Career gap penalization    — gaps for caregiving, health, personal reasons
  3. Geographic bias            — location as proxy for quality
  4. Pedigree bias              — previous employer prestige vs. actual output
  5. Recency bias               — penalizing older technologies unfairly
  6. Underrepresented talent    — hidden gems in non-obvious backgrounds

The correction applies BEFORE final scoring to produce a capability-first ranking.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ─── Bias Detection ──────────────────────────────────────────

PRESTIGE_COMPANIES = {
    "google", "meta", "amazon", "apple", "microsoft", "netflix",
    "openai", "deepmind", "stripe", "airbnb", "uber", "lyft",
    "goldman sachs", "mckinsey", "bain", "bcg"
}

TIER1_COLLEGES = {
    "iit", "iim", "bits pilani", "nit trichy", "stanford",
    "mit", "harvard", "oxford", "cambridge", "berkeley",
    "iit bombay", "iit delhi", "iit madras", "ntu", "nus"
}

HIGH_BIAS_RISK_PATTERNS = [
    "career break", "gap", "family", "caretaker", "health",
    "personal reasons", "freelance"
]

UNDERREPRESENTED_SIGNALS = [
    "self-taught", "bootcamp", "tier3", "tier-3", "no degree",
    "open source", "independent", "africa", "nigeria", "kenya",
    "ghana", "pakistan", "bangladesh", "south america", "argentina",
    "latam", "mexico", "vietnam"
]


def detect_bias_signals(candidate: dict) -> dict[str, Any]:
    """
    Analyze a candidate profile for potential bias factors.
    Returns detected biases and suggested corrections.
    """
    bias_flags = []
    adjustment = 0.0

    edu_tier = (candidate.get("education_tier") or "").lower()
    edu_detail = (candidate.get("education_detail") or "").lower()
    summary = (candidate.get("summary") or "").lower()
    headline = (candidate.get("headline") or "").lower()
    location = (candidate.get("location") or "").lower()
    career = candidate.get("career_history", [])
    cap = candidate.get("capability_profile", {})

    # ── 1. Prestige Halo Bias ─────────────────────────────────
    company_names = [r.get("company", "").lower() for r in career]
    prestige_companies_found = [
        c for c in company_names
        if any(p in c for p in PRESTIGE_COMPANIES)
    ]

    if prestige_companies_found:
        # Check if impact scores justify the prestige
        prestige_roles = [r for r in career if any(p in r.get("company", "").lower() for p in PRESTIGE_COMPANIES)]
        avg_prestige_impact = sum(r.get("impact_score", 0.5) for r in prestige_roles) / len(prestige_roles)

        if avg_prestige_impact < 0.65:
            bias_flags.append("prestige_halo_detected")
            adjustment -= 3.0  # Prestige company, average impact — reduce FAANG premium
        # Note: high-impact FAANG is genuinely impressive — no negative adjustment needed

    # ── 2. College Prestige Bias ─────────────────────────────
    is_tier1 = edu_tier == "tier1" or any(c in edu_detail for c in TIER1_COLLEGES)
    is_tier3_or_below = edu_tier in ("tier3", "bootcamp", "self-taught")

    if is_tier3_or_below:
        # Check if achievements compensate
        achievement_count = len(candidate.get("achievements", []))
        avg_impact = sum(r.get("impact_score", 0.5) for r in career) / max(len(career), 1)

        if avg_impact >= 0.80 or achievement_count >= 3:
            bias_flags.append("pedigree_bias_correction_applied")
            adjustment += 6.0  # High performer from non-prestige background
        elif avg_impact >= 0.65:
            bias_flags.append("pedigree_bias_correction_applied")
            adjustment += 3.0

    # ── 3. Career Gap Penalization ───────────────────────────
    gap_companies = [r for r in career if any(kw in (r.get("company", "") + r.get("description", "")).lower() for kw in HIGH_BIAS_RISK_PATTERNS)]

    if gap_companies:
        bias_flags.append("career_gap_detected_contextualized")
        # Look for evidence of continued learning during gap
        gap_descriptions = " ".join([r.get("description", "") for r in gap_companies]).lower()
        if any(kw in gap_descriptions for kw in ["certified", "contributed", "open source", "study", "course"]):
            adjustment += 4.0  # Productive gap — significant positive adjustment
            bias_flags.append("gap_productive_learning_detected")
        else:
            adjustment += 2.0  # Standard gap contextualization

    # ── 4. Geographic Bias ───────────────────────────────────
    underrepresented_geo = any(
        loc in location for loc in [
            "nigeria", "kenya", "ghana", "pakistan", "bangladesh",
            "ethiopia", "tanzania", "argentina", "colombia", "vietnam"
        ]
    )
    if underrepresented_geo:
        bias_flags.append("geographic_underrepresentation_detected")
        adjustment += 3.0  # Positive signal: succeeding from underrepresented geography

    # ── 5. Self-Taught / Bootcamp Bias ──────────────────────
    if any(sig in summary + headline + edu_detail for sig in UNDERREPRESENTED_SIGNALS):
        # Has the candidate demonstrated strong outcomes despite non-traditional path?
        outcomes = candidate.get("achievements", [])
        if outcomes:
            bias_flags.append("non_traditional_path_high_achiever")
            adjustment += 5.0

    # ── Compute Bias Risk Score ──────────────────────────────
    bias_risk_score = min(1.0, len(bias_flags) * 0.2)

    return {
        "bias_flags": bias_flags,
        "raw_adjustment": round(adjustment, 1),
        "bias_risk_score": round(bias_risk_score, 2),
        "has_prestige_halo": "prestige_halo_detected" in bias_flags,
        "has_gap_penalty": "career_gap_detected_contextualized" in bias_flags,
        "has_pedigree_correction": "pedigree_bias_correction_applied" in bias_flags,
        "has_geo_correction": "geographic_underrepresentation_detected" in bias_flags,
        "recommendation": _bias_recommendation(bias_flags),
    }


def apply_bias_correction(base_score: float, bias_analysis: dict) -> float:
    """
    Apply bias correction to a base score.
    Caps the total score at 100.
    """
    adjusted = base_score + bias_analysis.get("raw_adjustment", 0.0)
    return max(0.0, min(100.0, adjusted))


def _bias_recommendation(bias_flags: list[str]) -> str:
    """Generate a human-readable bias recommendation."""
    recommendations = []

    if "prestige_halo_detected" in bias_flags:
        recommendations.append(
            "FAANG/prestige company detected but impact scores are average — "
            "evaluate actual output, not employer name."
        )
    if "pedigree_bias_correction_applied" in bias_flags:
        recommendations.append(
            "Tier-3/bootcamp background with strong impact scores — "
            "capability evidence outweighs pedigree. Positive correction applied."
        )
    if "career_gap_detected_contextualized" in bias_flags:
        recommendations.append(
            "Career gap detected. Context: personal/family. "
            "Evaluate capability signals from before/after, not the gap itself."
        )
    if "gap_productive_learning_detected" in bias_flags:
        recommendations.append(
            "Gap was used productively (certifications/OSS contributions). "
            "This is a positive signal of self-driven learning."
        )
    if "geographic_underrepresentation_detected" in bias_flags:
        recommendations.append(
            "Candidate from underrepresented geography. "
            "Success in limited-resource environment is a strong capability signal."
        )
    if "non_traditional_path_high_achiever" in bias_flags:
        recommendations.append(
            "Non-traditional educational background with demonstrated achievements. "
            "Path to outcomes matters more than path taken."
        )

    if not recommendations:
        return "No significant bias signals detected. Standard evaluation applies."

    return " | ".join(recommendations)


def compute_fairness_score(bias_analysis: dict) -> float:
    """
    Compute a fairness score (0-1) indicating how bias-free this candidate's
    evaluation is likely to be in a standard ATS.
    0 = highly likely to be biased against, 1 = neutral
    """
    flags = bias_analysis.get("bias_flags", [])
    negative_flags = [
        f for f in flags
        if "correction_applied" not in f and "detected" in f and "productive" not in f
    ]
    correction_flags = [f for f in flags if "correction" in f or "productive" in f]

    # Standard ATS would penalize for: gaps, non-prestige education, geography
    penalty_count = len(negative_flags)
    benefit_count = len(correction_flags)

    fairness = 1.0 - (penalty_count * 0.15) + (benefit_count * 0.1)
    return max(0.1, min(1.0, fairness))
