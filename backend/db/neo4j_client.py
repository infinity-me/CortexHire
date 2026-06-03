"""
CortexHire — Neo4j Graph Database Client
Manages Candidate Life Graphs: career nodes, skill nodes, relationship edges.

Graph schema:
  (Person)-[:WORKED_AT {start, end, title, team_size}]->(Company)
  (Person)-[:USED_SKILL {proficiency}]->(Skill)
  (Person)-[:BUILT]->(Project)
  (Person)-[:LED_TEAM {size}]->(Team)
  (Person)-[:TRANSITIONED_TO]->(Domain)
  (Person)-[:ACHIEVED]->(Achievement)
"""
from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from neo4j import AsyncDriver

from config import settings

logger = logging.getLogger(__name__)


class Neo4jStore:
    def __init__(self) -> None:
        self._driver: "AsyncDriver | None" = None

    async def connect(self) -> None:
        if not settings.neo4j_enabled:
            logger.info("Neo4j disabled (NEO4J_ENABLED=false). Graph features skipped.")
            return
        try:
            from neo4j import AsyncGraphDatabase  # lazy import
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            await self._driver.verify_connectivity()
            await self._create_constraints()
            logger.info("Neo4j connected.")
        except Exception as e:
            logger.warning(f"Neo4j connection failed (graph features disabled): {e}")
            self._driver = None

    async def _create_constraints(self) -> None:
        if not self._driver:
            return
        async with self._driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE",
            ]
            for q in constraints:
                try:
                    await session.run(q)
                except Exception:
                    pass

    async def create_candidate_graph(self, candidate: dict[str, Any]) -> None:
        """Build the Candidate Life Graph from structured profile data."""
        if not self._driver:
            return
        async with self._driver.session() as session:
            # Create Person node
            await session.run(
                """
                MERGE (p:Person {id: $id})
                SET p.name = $name,
                    p.headline = $headline,
                    p.location = $location,
                    p.years_experience = $years_experience,
                    p.education_tier = $education_tier
                """,
                id=candidate["id"],
                name=candidate.get("name", ""),
                headline=candidate.get("headline", ""),
                location=candidate.get("location", ""),
                years_experience=candidate.get("years_experience", 0),
                education_tier=candidate.get("education_tier", ""),
            )

            # Create Company nodes and WORKED_AT edges
            for role in candidate.get("career_history", []):
                await session.run(
                    """
                    MERGE (c:Company {name: $company})
                    SET c.industry = $industry, c.size = $size, c.type = $type
                    WITH c
                    MATCH (p:Person {id: $person_id})
                    MERGE (p)-[r:WORKED_AT {title: $title}]->(c)
                    SET r.start_year = $start_year,
                        r.end_year = $end_year,
                        r.team_size = $team_size,
                        r.impact_score = $impact_score
                    """,
                    company=role.get("company", "Unknown"),
                    industry=role.get("industry", ""),
                    size=role.get("company_size", ""),
                    type=role.get("company_type", ""),
                    person_id=candidate["id"],
                    title=role.get("title", ""),
                    start_year=role.get("start_year", 0),
                    end_year=role.get("end_year", 0),
                    team_size=role.get("team_size", 0),
                    impact_score=role.get("impact_score", 0.5),
                )

            # Create Skill nodes and USED_SKILL edges
            for skill in candidate.get("skills", []):
                skill_name = skill if isinstance(skill, str) else skill.get("name", "")
                proficiency = 0.7 if isinstance(skill, str) else skill.get("proficiency", 0.7)
                await session.run(
                    """
                    MERGE (s:Skill {name: $name})
                    WITH s
                    MATCH (p:Person {id: $person_id})
                    MERGE (p)-[r:USED_SKILL]->(s)
                    SET r.proficiency = $proficiency
                    """,
                    name=skill_name,
                    person_id=candidate["id"],
                    proficiency=proficiency,
                )

    async def get_candidate_graph(self, candidate_id: str) -> dict[str, Any]:
        """Retrieve the full life graph for a candidate."""
        if not self._driver:
            return {}
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (p:Person {id: $id})
                OPTIONAL MATCH (p)-[r:WORKED_AT]->(c:Company)
                OPTIONAL MATCH (p)-[rs:USED_SKILL]->(s:Skill)
                RETURN p,
                       collect(DISTINCT {company: c.name, title: r.title,
                                         start: r.start_year, end: r.end_year,
                                         team_size: r.team_size, impact: r.impact_score}) as roles,
                       collect(DISTINCT {skill: s.name, proficiency: rs.proficiency}) as skills
                """,
                id=candidate_id,
            )
            record = await result.single()
            if not record:
                return {}
            return {
                "person": dict(record["p"]),
                "roles": record["roles"],
                "skills": record["skills"],
            }

    async def get_career_trajectory(self, candidate_id: str) -> list[dict]:
        """Get ordered career history for temporal analysis."""
        if not self._driver:
            return []
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (p:Person {id: $id})-[r:WORKED_AT]->(c:Company)
                RETURN r.title as title, c.name as company, c.type as type,
                       r.start_year as start_year, r.end_year as end_year,
                       r.team_size as team_size, r.impact_score as impact_score
                ORDER BY r.start_year ASC
                """,
                id=candidate_id,
            )
            return [dict(record) async for record in result]

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()


# Singleton
neo4j_store = Neo4jStore()
