"""
Procedural Memory
=================

Encoded skills and capabilities.

Stores:
- How to do things
- Skills and procedures
- Capabilities
- Action patterns

Like muscle memory - knowledge of HOW rather than WHAT.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from sarai.types import Experience, Query
from sarai.safety.logging import ComprehensiveLogger


@dataclass
class Skill:
    """A learned skill or capability."""
    skill_id: str
    name: str
    description: str
    procedure: List[str]  # Steps to execute
    proficiency: float  # 0-1, how well mastered
    usage_count: int
    last_used: datetime
    success_rate: float  # 0-1


class ProceduralMemory:
    """
    Procedural memory storage and retrieval.

    Stores skills, capabilities, and procedural knowledge.
    """

    def __init__(self, storage_path: str, logger: ComprehensiveLogger):
        """
        Initialize procedural memory.

        Args:
            storage_path: Path for memory storage
            logger: Comprehensive logger
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        # In-memory skill index
        self.skills: Dict[str, Skill] = {}

        # Load from disk
        self._load_from_disk()

        self.logger.logger.info(
            f"Procedural memory initialized with {len(self.skills)} skills"
        )

    async def store_skill(self, experience: Experience) -> str:
        """
        Store a skill from an experience.

        Args:
            experience: Experience containing skill learning

        Returns:
            Skill ID
        """
        # Extract skill information
        skill_name = experience.context.get("skill_name", "unknown_skill")
        skill_id = f"skill_{len(self.skills)}_{skill_name.replace(' ', '_')}"

        skill = Skill(
            skill_id=skill_id,
            name=skill_name,
            description=experience.context.get("skill_description", ""),
            procedure=experience.context.get("procedure", []),
            proficiency=0.5,  # Start at novice level
            usage_count=0,
            last_used=datetime.now(),
            success_rate=1.0  # Optimistic start
        )

        self.skills[skill_id] = skill

        # Save to disk
        self._save_to_disk()

        self.logger.logger.debug(f"Stored skill: {skill_name}")

        return skill_id

    async def recall(self, query: Query) -> List[Skill]:
        """
        Retrieve skills matching query.

        Args:
            query: The query

        Returns:
            List of matching skills
        """
        matches = []

        query_text = query.content.lower()

        for skill in self.skills.values():
            # Match by name or description
            if (query_text in skill.name.lower() or
                query_text in skill.description.lower()):
                matches.append(skill)

        # Sort by proficiency
        matches.sort(key=lambda s: s.proficiency, reverse=True)

        return matches[:query.max_results]

    def use_skill(self, skill_id: str, success: bool):
        """
        Record skill usage.

        Updates proficiency and success rate.

        Args:
            skill_id: The skill being used
            success: Whether usage was successful
        """
        if skill_id not in self.skills:
            return

        skill = self.skills[skill_id]

        # Update usage count
        skill.usage_count += 1
        skill.last_used = datetime.now()

        # Update success rate (exponential moving average)
        alpha = 0.1  # Learning rate
        skill.success_rate = (
            alpha * (1.0 if success else 0.0) +
            (1 - alpha) * skill.success_rate
        )

        # Update proficiency based on usage and success
        if success:
            # Increase proficiency with successful use (but diminishing returns)
            skill.proficiency = min(
                skill.proficiency + 0.05 * (1 - skill.proficiency),
                1.0
            )
        else:
            # Slight decrease with failure
            skill.proficiency = max(skill.proficiency - 0.02, 0.0)

        self.logger.logger.debug(
            f"Skill {skill.name} used: proficiency now {skill.proficiency:.2f}"
        )

        self._save_to_disk()

    async def consolidate(self):
        """
        Consolidation during sleep.

        - Strengthen frequently used skills
        - Degrade unused skills
        - Remove completely forgotten skills
        """
        cutoff_date = datetime.now() - timedelta(days=60)
        removed = []

        for skill_id, skill in list(self.skills.items()):
            # Degrade unused skills
            if skill.last_used < cutoff_date:
                skill.proficiency *= 0.95

                # Remove if proficiency very low
                if skill.proficiency < 0.1:
                    removed.append(skill_id)
                    del self.skills[skill_id]

        self.logger.logger.info(
            f"Procedural consolidation: removed {len(removed)} unused skills"
        )

        self._save_to_disk()

    async def clear(self):
        """Clear all procedural memory."""
        self.skills.clear()

        skills_file = self.storage_path / "skills.json"
        if skills_file.exists():
            skills_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        if not self.skills:
            return {
                "total_skills": 0,
                "avg_proficiency": 0,
                "avg_success_rate": 0
            }

        return {
            "total_skills": len(self.skills),
            "avg_proficiency": sum(s.proficiency for s in self.skills.values()) / len(self.skills),
            "avg_success_rate": sum(s.success_rate for s in self.skills.values()) / len(self.skills),
            "most_used": self._get_most_used_skills(),
            "highest_proficiency": self._get_highest_proficiency_skills()
        }

    def _get_most_used_skills(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently used skills."""
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: s.usage_count,
            reverse=True
        )

        return [
            {"name": s.name, "usage_count": s.usage_count}
            for s in sorted_skills[:n]
        ]

    def _get_highest_proficiency_skills(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get highest proficiency skills."""
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: s.proficiency,
            reverse=True
        )

        return [
            {"name": s.name, "proficiency": s.proficiency}
            for s in sorted_skills[:n]
        ]

    def _load_from_disk(self):
        """Load skills from disk."""
        skills_file = self.storage_path / "skills.json"

        if not skills_file.exists():
            return

        try:
            with open(skills_file, 'r') as f:
                data = json.load(f)

                for skill_data in data:
                    skill_data['last_used'] = datetime.fromisoformat(skill_data['last_used'])
                    skill = Skill(**skill_data)
                    self.skills[skill.skill_id] = skill

        except Exception as e:
            self.logger.log_error(e, {"context": "loading procedural memory"})

    def _save_to_disk(self):
        """Save skills to disk."""
        skills_file = self.storage_path / "skills.json"

        try:
            data = []
            for skill in self.skills.values():
                skill_dict = asdict(skill)
                skill_dict['last_used'] = skill.last_used.isoformat()
                data.append(skill_dict)

            with open(skills_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.log_error(e, {"context": "saving procedural memory"})


from datetime import timedelta  # Add missing import
