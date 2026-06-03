"""
CortexHire — Innovation #7: Temporal Intelligence

Models career momentum over time. Two candidates with the same experience level
may have radically different trajectories — one accelerating, one plateauing.

Signals analyzed:
  - Year-over-year scope expansion
  - Promotion velocity
  - Impact score progression
  - Company stage progression (startup → scale → enterprise or vice versa)
  - Skill acquisition rate
  - Team size growth trajectory
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def compute_temporal_profile(candidate: dict) -> dict[str, Any]:
    """
    Analyze career history to extract temporal intelligence:
    momentum, trajectory type, acceleration curve.
    """
    career = candidate.get("career_history", [])
    if not career:
        return _empty_temporal_profile()

    # Sort by start year
    career_sorted = sorted(career, key=lambda r: r.get("start_year", 0))

    # ── Metrics per role ──────────────────────────────────────
    years_at_role = []
    impact_scores = []
    team_sizes = []
    company_types = []

    for i, role in enumerate(career_sorted):
        start = role.get("start_year", 0)
        end = role.get("end_year", start + 1)
        if end == 0:
            end = start + 1

        duration = max(end - start, 0.5)
        years_at_role.append(duration)
        impact_scores.append(role.get("impact_score", 0.5))
        team_sizes.append(role.get("team_size", 0))
        company_types.append(role.get("company_type", "unknown"))

    # ── Trajectory Analysis ──────────────────────────────────

    # Impact trend: is performance improving?
    impact_trend = 0.0
    if len(impact_scores) > 1:
        deltas = [impact_scores[i+1] - impact_scores[i] for i in range(len(impact_scores)-1)]
        impact_trend = sum(deltas) / len(deltas)

    # Team size trend: is scope growing?
    max_team = max(team_sizes) if team_sizes else 0
    team_growth = 0.0
    if len(team_sizes) > 1:
        deltas = [team_sizes[i+1] - team_sizes[i] for i in range(len(team_sizes)-1)]
        team_growth = sum(deltas) / len(deltas)

    # Tenure trend: staying shorter = more in demand / promoted faster?
    avg_tenure = sum(years_at_role) / len(years_at_role) if years_at_role else 0
    # Optimal tenure: 1.5–3 years per role shows progression
    tenure_score = _score_tenure_pattern(years_at_role)

    # Startup progression
    startup_stages = [ct for ct in company_types if ct in ("startup", "startup-scale")]
    startup_ratio = len(startup_stages) / len(company_types) if company_types else 0

    # Average impact score
    avg_impact = sum(impact_scores) / len(impact_scores) if impact_scores else 0.5

    # Latest vs earliest impact
    impact_momentum = impact_scores[-1] - impact_scores[0] if len(impact_scores) > 1 else 0

    # ── Trajectory Classification ────────────────────────────

    trajectory = _classify_trajectory(impact_trend, team_growth, impact_momentum, avg_tenure)

    # ── Momentum Score (0–1) ─────────────────────────────────

    momentum_score = _compute_momentum_score(
        impact_trend=impact_trend,
        team_growth=team_growth,
        avg_impact=avg_impact,
        tenure_score=tenure_score,
        years_experience=candidate.get("years_experience", 0),
    )

    # ── Data points for frontend chart ──────────────────────

    data_points = []
    for i, role in enumerate(career_sorted):
        data_points.append({
            "year": role.get("start_year", 2015 + i),
            "company": role.get("company", "Unknown"),
            "title": role.get("title", ""),
            "impact_score": role.get("impact_score", 0.5),
            "team_size": role.get("team_size", 0),
            "company_type": role.get("company_type", "unknown"),
        })

    return {
        "trajectory": trajectory,
        "momentum_score": round(momentum_score, 3),
        "impact_trend": round(impact_trend, 3),
        "team_growth_trend": round(team_growth, 2),
        "avg_tenure_years": round(avg_tenure, 1),
        "max_team_led": max_team,
        "avg_impact_score": round(avg_impact, 3),
        "impact_momentum": round(impact_momentum, 3),
        "startup_affinity": round(startup_ratio, 2),
        "data_points": data_points,
        "total_roles": len(career_sorted),
    }


def _classify_trajectory(
    impact_trend: float,
    team_growth: float,
    impact_momentum: float,
    avg_tenure: float,
) -> str:
    """Classify career trajectory as accelerating, steady, plateauing, or declining."""
    score = 0
    if impact_trend > 0.05:
        score += 2
    elif impact_trend > 0:
        score += 1
    elif impact_trend < -0.05:
        score -= 2

    if team_growth > 2:
        score += 2
    elif team_growth > 0:
        score += 1
    elif team_growth < -2:
        score -= 1

    if impact_momentum > 0.15:
        score += 2
    elif impact_momentum > 0:
        score += 1
    elif impact_momentum < -0.1:
        score -= 1

    if avg_tenure < 1.5:
        score -= 1  # Might be job-hopping
    elif 1.5 <= avg_tenure <= 3:
        score += 1

    if score >= 4:
        return "accelerating"
    elif score >= 1:
        return "steady"
    elif score >= -1:
        return "plateauing"
    else:
        return "declining"


def _score_tenure_pattern(years_at_role: list[float]) -> float:
    """Score tenure pattern — optimal is 1.5–3 years per role."""
    if not years_at_role:
        return 0.5
    scores = []
    for tenure in years_at_role:
        if 1.5 <= tenure <= 3.0:
            scores.append(1.0)
        elif 1.0 <= tenure < 1.5 or 3.0 < tenure <= 4.0:
            scores.append(0.75)
        elif tenure < 1.0:
            scores.append(0.4)  # Possibly job-hopping
        else:
            scores.append(0.6)  # Long-tenured, possibly plateauing
    return sum(scores) / len(scores)


def _compute_momentum_score(
    impact_trend: float,
    team_growth: float,
    avg_impact: float,
    tenure_score: float,
    years_experience: float,
) -> float:
    """Compute normalized career momentum score (0–1)."""
    # Normalize impact_trend (typically -0.3 to +0.3)
    norm_impact_trend = max(0.0, min(1.0, (impact_trend + 0.3) / 0.6))

    # Normalize team growth (typically -5 to +15)
    norm_team_growth = max(0.0, min(1.0, (team_growth + 5) / 20))

    # Years experience bonus: junior with high trajectory > senior with low
    exp_modifier = 1.0
    if years_experience <= 3:
        exp_modifier = 1.15  # Boost for early-career accelerators
    elif years_experience >= 10:
        exp_modifier = 0.95  # Slight penalty for long careers with slow growth

    raw = (
        norm_impact_trend * 0.35 +
        norm_team_growth * 0.20 +
        avg_impact * 0.30 +
        tenure_score * 0.15
    ) * exp_modifier

    return max(0.0, min(1.0, raw))


def _empty_temporal_profile() -> dict:
    return {
        "trajectory": "unknown",
        "momentum_score": 0.5,
        "impact_trend": 0.0,
        "team_growth_trend": 0.0,
        "avg_tenure_years": 0.0,
        "max_team_led": 0,
        "avg_impact_score": 0.5,
        "impact_momentum": 0.0,
        "startup_affinity": 0.0,
        "data_points": [],
        "total_roles": 0,
    }
