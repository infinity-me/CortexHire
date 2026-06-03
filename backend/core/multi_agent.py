"""
CortexHire — Innovation #4: Multi-Agent Recruiter Simulation

The crown jewel of CortexHire. Runs 5 specialized AI recruiter agents in parallel,
each with a distinct expertise and evaluation rubric. Their assessments are aggregated
by the Consensus Ranking Engine.

The 5 Agents:
  1. Technical Recruiter    — assesses technical depth, complexity handled, architecture
  2. Hiring Manager         — assesses execution risk, ownership, delivery
  3. Org. Psychologist      — reads behavioral patterns, resilience, adaptability
  4. Bias Corrector         — detects and corrects pedigree/gap/geographic bias
  5. Future Predictor       — projects 2-year trajectory, leadership emergence

Each agent returns:
  - score (0–100)
  - confidence (0–1)
  - key_signals (list of evidence points)
  - risks (list of concerns)
  - reasoning (text)
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from core.llm_router import llm_chat

logger = logging.getLogger(__name__)


# ─── Agent Prompts ──────────────────────────────────────────

TECHNICAL_RECRUITER_SYSTEM = """
You are a world-class Technical Recruiter with 15 years of experience hiring backend, 
infrastructure, and ML engineers at top-tier companies.

Your job: Evaluate a candidate's technical capability against a role's technical requirements.
Focus ONLY on technical signals — not personality, not potential, not culture fit.

Evaluate:
1. Complexity of systems built (simple CRUD vs. distributed systems at scale)
2. Depth of technical expertise in required domains
3. Evidence of debugging, architecture, and system design capability
4. Scale of technical problems handled (users, data volume, throughput)
5. Quality and credibility of technical achievements

Return a JSON object with EXACTLY these fields:
{
  "agent": "Technical Recruiter",
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "key_signals": [<list of 3-5 specific technical evidence points>],
  "risks": [<list of 1-3 technical concerns>],
  "reasoning": "<2-3 sentences of technical assessment>"
}
"""

HIRING_MANAGER_SYSTEM = """
You are a seasoned Hiring Manager who has built and led engineering teams at startups and scale-ups.
You know what separates engineers who deliver from those who write code but miss outcomes.

Your job: Evaluate whether a candidate can execute in this specific role.
Focus on: ownership, delivery track record, autonomy, stakeholder management, and outcome orientation.

Evaluate:
1. Evidence of owning outcomes (not just completing tasks)
2. Delivery under pressure and in ambiguity
3. Communication and stakeholder management signals
4. Track record of promotions / scope expansion (proxy for performance)
5. Risk of underperforming in the specific role context

Return a JSON object with EXACTLY these fields:
{
  "agent": "Hiring Manager",
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "key_signals": [<list of 3-5 specific execution evidence points>],
  "risks": [<list of 1-3 execution/delivery concerns>],
  "reasoning": "<2-3 sentences of execution assessment>"
}
"""

ORG_PSYCHOLOGIST_SYSTEM = """
You are an Organizational Psychologist specializing in workplace behavior, resilience, and culture fit.
You have evaluated thousands of candidates across different company stages and cultures.

Your job: Evaluate a candidate's behavioral profile and cultural alignment.
Focus on: resilience, adaptability, consistency, self-awareness, and team dynamics.

Evaluate:
1. Resilience patterns (handled adversity, career challenges, setbacks)
2. Adaptability (domain switches, company stage transitions, role pivots)
3. Consistency patterns (stable performer vs. erratic)
4. Self-awareness signals (career choices, pivots, self-presentation)
5. Cultural fit for the specific team dynamics described

Return a JSON object with EXACTLY these fields:
{
  "agent": "Organizational Psychologist",
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "key_signals": [<list of 3-5 behavioral evidence points>],
  "risks": [<list of 1-2 behavioral/cultural concerns>],
  "reasoning": "<2-3 sentences of behavioral assessment>"
}
"""

BIAS_CORRECTOR_SYSTEM = """
You are an AI Fairness Specialist responsible for detecting and correcting hiring bias.
Your purpose: ensure candidates are evaluated on CAPABILITY signals, not PRIVILEGE signals.

Common bias patterns to detect and correct:
1. College prestige bias (IIT/FAANG premium unrelated to actual capability)
2. Career gap penalization (gaps due to caregiving, health, personal reasons)
3. Geographic bias (assuming quality based on country/city)
4. Resume formatting bias (judging by presentation, not content)
5. Company name halo effect (previous employer prestige vs. actual work quality)
6. Gender-coded language bias in self-description

Your job:
1. Identify bias signals present in how this candidate might be evaluated
2. Assess the candidate's INTRINSIC capability after removing privilege signals
3. Apply a score adjustment (positive for under-privileged high performers, minimal for pedigreed average performers)

Return a JSON object with EXACTLY these fields:
{
  "agent": "Diversity & Bias Corrector",
  "score": <0-100, bias-adjusted score>,
  "confidence": <0.0-1.0>,
  "bias_flags_detected": [<list of bias types detected, empty if none>],
  "bias_adjustment": <-10 to +15, the adjustment applied to raw capability score>,
  "adjusted_score": <the bias-corrected final score>,
  "key_signals": [<list of 3-5 intrinsic capability evidence points>],
  "reasoning": "<2-3 sentences explaining the bias analysis and correction>"
}
"""

FUTURE_PREDICTOR_SYSTEM = """
You are a Future Potential Predictor — a specialist in identifying human trajectory and growth curves.
You predict where a candidate will be in 2 years, not where they are today.

Elite recruiters know: hiring for current state is mediocre. Hiring for trajectory is elite.

Your job: Analyze a candidate's career arc and predict their future capability.
Focus on:
1. Year-over-year scope expansion (are they growing faster than peers?)
2. Learning velocity (how quickly do they pick up new domains/skills?)
3. Leadership emergence signals (are they developing influence?)
4. Trajectory type: accelerating / steady / plateauing / declining
5. 2-year prediction: where will they be?

Return a JSON object with EXACTLY these fields:
{
  "agent": "Future Potential Predictor",
  "score": <0-100, score based on predicted future capability>,
  "confidence": <0.0-1.0>,
  "trajectory": <"accelerating" | "steady" | "plateauing" | "declining">,
  "predicted_role_in_2_years": "<predicted title or scope>",
  "learning_velocity": <0.0-1.0>,
  "leadership_emergence": <0.0-1.0>,
  "key_signals": [<list of 3-5 trajectory evidence points>],
  "reasoning": "<2-3 sentences predicting future growth>"
}
"""


def _build_evaluation_context(candidate: dict, job: dict, role_genome: dict) -> str:
    """Build rich context for agent evaluation."""
    career_text = "\n".join([
        f"  - {r.get('title', '')} @ {r.get('company', '')} ({r.get('start_year', '')}-{r.get('end_year', '')}) | "
        f"Team: {r.get('team_size', 0)} | Impact: {r.get('impact_score', 0):.2f}\n"
        f"    {r.get('description', '')}"
        for r in candidate.get("career_history", [])
    ])

    skills_text = ", ".join([
        s["name"] if isinstance(s, dict) else s
        for s in candidate.get("skills", [])
    ])

    achievements_text = "\n".join([f"  • {a}" for a in candidate.get("achievements", [])])

    cap = candidate.get("capability_profile", {})

    return f"""
CANDIDATE PROFILE:
Name: {candidate.get('name', 'N/A')}
Headline: {candidate.get('headline', 'N/A')}
Location: {candidate.get('location', 'N/A')}
Years Experience: {candidate.get('years_experience', 0)}
Education: {candidate.get('education_detail', 'N/A')} (Tier: {candidate.get('education_tier', 'N/A')})

Summary: {candidate.get('summary', 'N/A')}

Career History:
{career_text}

Skills: {skills_text}

Key Achievements:
{achievements_text}

Capability Profile (self-assessed):
  Technical Depth: {cap.get('technical_depth', 0):.2f}
  Adaptability: {cap.get('adaptability', 0):.2f}
  Leadership: {cap.get('leadership', 0):.2f}
  Execution: {cap.get('execution', 0):.2f}
  Systems Thinking: {cap.get('systems_thinking', 0):.2f}
  Creativity: {cap.get('creativity', 0):.2f}
  Resilience: {cap.get('resilience', 0):.2f}
  Communication: {cap.get('communication', 0):.2f}

ROLE REQUIREMENTS:
Job Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')} ({job.get('seniority', 'N/A')})

Role Genome (AI-extracted requirements):
  Technical Depth Required: {role_genome.get('technical_depth', 0):.2f}
  Ambiguity Tolerance Required: {role_genome.get('ambiguity_tolerance', 0):.2f}
  Ownership Expected: {role_genome.get('ownership', 0):.2f}
  Communication Required: {role_genome.get('communication', 0):.2f}
  Startup Readiness: {role_genome.get('startup_readiness', 0):.2f}
  Leadership Expected: {role_genome.get('leadership_potential', 0):.2f}
  Creativity Required: {role_genome.get('creativity', 0):.2f}
  Execution Speed: {role_genome.get('execution_speed', 0):.2f}

Functional Needs: {', '.join(role_genome.get('functional_needs', []))}
Hidden Needs: {', '.join(role_genome.get('hidden_needs', []))}
Team Dynamics: {role_genome.get('team_dynamics', '')}
Cognitive Style: {role_genome.get('cognitive_style', '')}
""".strip()


async def run_agent(
    agent_name: str,
    system_prompt: str,
    context: str,
    task_name: str,
) -> dict[str, Any]:
    """Run a single recruiter agent and return its assessment."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Evaluate this candidate for the role:\n\n{context}"},
    ]
    try:
        raw = await llm_chat(
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            json_mode=True,
            task_name=task_name,
        )
        result = json.loads(raw)
        result["agent"] = agent_name
        return result
    except Exception as e:
        logger.warning(f"Agent {agent_name} failed: {e}")
        return {
            "agent": agent_name,
            "score": 60.0,
            "confidence": 0.5,
            "key_signals": ["Agent evaluation unavailable"],
            "risks": ["Insufficient data for assessment"],
            "reasoning": f"Agent evaluation failed: {str(e)[:100]}",
        }


async def run_all_agents(
    candidate: dict,
    job: dict,
    role_genome: dict,
) -> list[dict[str, Any]]:
    """
    Run all 5 recruiter agents in PARALLEL for maximum efficiency.
    Returns list of agent assessments.
    """
    context = _build_evaluation_context(candidate, job, role_genome)

    agents = [
        ("Technical Recruiter", TECHNICAL_RECRUITER_SYSTEM, "technical_recruiter"),
        ("Hiring Manager", HIRING_MANAGER_SYSTEM, "hiring_manager"),
        ("Organizational Psychologist", ORG_PSYCHOLOGIST_SYSTEM, "org_psychologist"),
        ("Diversity & Bias Corrector", BIAS_CORRECTOR_SYSTEM, "bias_corrector"),
        ("Future Potential Predictor", FUTURE_PREDICTOR_SYSTEM, "future_predictor"),
    ]

    tasks = [
        run_agent(name, system_prompt, context, task_name)
        for name, system_prompt, task_name in agents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    agent_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Agent {agents[i][0]} raised exception: {result}")
            agent_results.append({
                "agent": agents[i][0],
                "score": 60.0,
                "confidence": 0.4,
                "key_signals": [],
                "risks": ["Evaluation unavailable"],
                "reasoning": "Agent encountered an error during evaluation.",
            })
        else:
            agent_results.append(result)

    logger.info(f"All 5 agents completed for {candidate.get('name', 'unknown')}")
    return agent_results
